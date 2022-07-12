window._DEBUGGER = function _DEBUGGER (error=null) {
    const place_breakpoint_here = 'use variable _locals in console to get locals() from python frame';
}

// utils
function isObject (obj) {
  return obj && typeof obj === 'object'
}

function mergeDeep(...objects) {
  return objects.reduce((acc, obj) => {
    Object.entries(obj).forEach(([key, objValue]) => {
      const accValue = acc[key]

      if (Array.isArray(accValue) && Array.isArray(objValue)) {
        acc[key] = accValue.concat(...objValue)
      } else if (isObject(accValue) && isObject(objValue)) {
        acc[key] = mergeDeep(accValue, objValue)
      } else {
        acc[key] = objValue
      }
    })

    return acc
  }, {})
}

async function delay(ms) {
  return new Promise(r => setTimeout(r, ms))
}

window.delay = delay


// console tools

function get_py_tag(i) {
    return () => window[`$${i}`]._py
}

Object.defineProperties(
    window,
    Object.fromEntries(new Array(10).fill(null).map(
        (_, i) => [`py${i}`, {get: get_py_tag(i)}]
    ))
)
/**
 * usage:
 * > py0
 * evaluates $0._py
 * available for py0-py9
 */

// pyweb config

// could be useful in the future, i.e: get attributes of <script src="pyweb" />
pyweb.script = document.currentScript

if (!document.title) {
    document.title = 'PyWeb'
    console.warn(`Document title is not set, use default title: ${document.title}`)
}
if (!window.pyweb || !window.pyweb.config) {
    console.warn(`
        No pyweb config found! Default config will be used
        If you have config, you must define it before loading pyweb script
    `)
    if (!window.pyweb) {
        window.pyweb = {}
    }
    if (!window.pyweb.config) {
        window.pyweb.config = {}
    }
}

const DEFAULT_CONFIG = {
    pyodide_version: '0.21.0a2',
    // use wrapper, so pyweb.__main__ could be overridden
    onload: () => pyweb.__main__(),
    // extra modules in base dir to load
    modules: [],
}

if (!pyweb.config.path && pyweb.script.src.indexOf('pyweb.js')) {
    pyweb.config.path = pyweb.script.src.substring(0, pyweb.script.src.indexOf('pyweb.js') - 1).replace(/\/+$/, '')
}

const config = mergeDeep(DEFAULT_CONFIG, pyweb.config)
pyweb.__CONFIG__ = config
pyweb._to_await = null
pyweb._async_to_sync = function _async_to_sync() {
    return (async () => {
        try {
            window.pyweb._to_await = await window.pyweb._to_await
        } catch (e) {
            window._DEBUGGER(e)
            console.error(e)
        }
    })()
}

// loading pyodide

const indexURL = `https://cdn.jsdelivr.net/pyodide/v${config.pyodide_version}/full/`
const script = document.createElement('script')
script.type = 'module'
script.src = indexURL + 'pyodide.js'
document.head.appendChild(script)


// defining tools for running python

pyweb.loadFile = async function loadFile (filePath) {
    pyweb.__CURRENT_LOADING_FILE__ = filePath
    return await (await fetch(filePath)).text()
}
pyweb._loadInternalFile = async function loadInternalFile (file) {
    pyodide.FS.writeFile(`pyweb/${file}`, await pyweb.loadFile(`${config.path}/pyweb/${file}`))
}
window.py = function runPython (...args) {
    try {
        return pyodide.runPython(...args)
    } catch (e) {
        console.debug(e)
        window._DEBUGGER(e)
        throw e
    }
}
window.apy = async function runPythonAsync (code, ...args) {
    await pyodide.loadPackagesFromImports(code)
    try {
        return await pyodide.runPythonAsync(code, ...args)
    } catch (e) {
        console.debug(e)
        window._DEBUGGER(e)
        throw e
    }
}
window.pyf = async function runPythonFile (filePath) {
    return window.py(await pyweb.loadFile(filePath))
}
window.apyf = async function runPythonAsyncFile (filePath) {
    return await window.apy(await pyweb.loadFile(filePath))
}

if (!pyweb.__main__) {
    pyweb.__main__ = () => {
        console.warn('You can override pyweb.__main__ to run code after pyweb finish loading')
    }
}

window.addEventListener('load', async function () {
    window.pyodide = await window.loadPyodide({ indexURL })
    await Promise.all([system_load(), pyweb_load()])
})


async function system_load() {
    await pyodide.loadPackage('micropip')
    py(`
import sys
print(sys.version)
del sys
`)
}

async function pyweb_load() {
    // load relative modules from pyweb/__init__.py
    pyodide.FS.mkdir('pyweb')
    const _init = await pyweb.loadFile(`${config.path}/pyweb/__init__.py`)
    const pyweb_modules = []
    for (const line of _init.split('\n')) {
        if (line.substring(0, 13) === 'from . import') {
            pyweb_modules.push(`${line.substring(14)}.py`)
        }
    }
    config.modules.unshift('__init__.py', ...pyweb_modules)

    // TODO: create wheel and load pyweb modules via pip
    await Promise.all(config.modules.map(
        file => pyweb._loadInternalFile(file)
    ))

    py(`
import pyweb
print('PyWeb version:', pyweb.__version__)
del pyweb
`)

    try {
        await apyf('./__init__.py')  // TODO: load ./__init__.py as internal?
    } catch (e) {
        console.info('You can add __init__.py near index.html to auto-load your code')
    }

    await config.onload()
}

Node.prototype.insertChild = function (child, index) {
    /**
     *
     * # Python version
     * # TODO: check why it's not working
     * @js_func()
     * def _node_insert_child(self: js.Element, child, index=None):
     *     if index is None or index >= len(self.children):
     *         self.appendChild(child)
     *     else:
     *         self.insertBefore(child, self.children[index])
     *
     * js.Node.prototype.insertChild = _node_insert_child
     */
    if (index == null || index >= this.children.length) {
        this.appendChild(child)
    } else {
        this.insertBefore(child, this.children[index])
    }
}

Node.prototype.safeRemoveChild = function (child) {
    if (this.contains(child)) {
        return this.removeChild(child)
    }
}
