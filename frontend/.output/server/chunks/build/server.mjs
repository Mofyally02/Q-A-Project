import process from 'node:process';globalThis._importMeta_=globalThis._importMeta_||{url:"file:///_entry.js",env:process.env};import { hasInjectionContext, getCurrentInstance, inject, defineComponent, createElementBlock, shallowRef, provide, cloneVNode, h, defineAsyncComponent, computed, useSSRContext, createApp, onServerPrefetch, ref, mergeProps, unref, toRef, onErrorCaptured, createVNode, resolveDynamicComponent, shallowReactive, reactive, effectScope, isReadonly, isRef, isShallow, isReactive, toRaw, toValue, getCurrentScope, markRaw, nextTick, onScopeDispose, watch, toRefs } from 'vue';
import { i as hasProtocol, k as isScriptProtocol, j as joinURL, w as withQuery, s as sanitizeStatusCode, l as getContext, $ as $fetch$1, m as baseURL, n as klona, o as defuFn, q as createHooks, e as createError$1, t as isEqual, v as stringifyParsedURL, x as stringifyQuery, y as parseQuery, z as toRouteMatcher, A as createRouter, B as defu } from '../nitro/nitro.mjs';
import { Icon, _api, addAPIProvider, setCustomIconsLoader, getIcon, loadIcon as loadIcon$1 } from '@iconify/vue';
import { ssrRenderAttrs, ssrRenderList, ssrInterpolate, ssrIncludeBooleanAttr, ssrRenderComponent, ssrRenderClass, ssrRenderAttr, ssrRenderStyle, ssrLooseContain, ssrLooseEqual, ssrRenderSuspense, ssrRenderVNode } from 'vue/server-renderer';
import { getIconCSS } from '@iconify/utils/lib/css/icon';
import { u as useHead$1, h as headSymbol, a as useSeoMeta$1 } from '../routes/renderer.mjs';
import 'node:http';
import 'node:https';
import 'node:events';
import 'node:buffer';
import 'node:fs';
import 'node:path';
import 'node:crypto';
import 'node:url';
import '@iconify/utils';
import 'consola';
import 'vue-bundle-renderer/runtime';
import 'unhead/server';
import 'devalue';
import 'unhead/plugins';
import 'unhead/utils';

//#region src/index.ts
const DEBOUNCE_DEFAULTS = { trailing: true };
/**
Debounce functions
@param fn - Promise-returning/async function to debounce.
@param wait - Milliseconds to wait before calling `fn`. Default value is 25ms
@returns A function that delays calling `fn` until after `wait` milliseconds have elapsed since the last time it was called.
@example
```
import { debounce } from 'perfect-debounce';
const expensiveCall = async input => input;
const debouncedFn = debounce(expensiveCall, 200);
for (const number of [1, 2, 3]) {
console.log(await debouncedFn(number));
}
//=> 1
//=> 2
//=> 3
```
*/
function debounce(fn, wait = 25, options = {}) {
	options = {
		...DEBOUNCE_DEFAULTS,
		...options
	};
	if (!Number.isFinite(wait)) throw new TypeError("Expected `wait` to be a finite number");
	let leadingValue;
	let timeout;
	let resolveList = [];
	let currentPromise;
	let trailingArgs;
	const applyFn = (_this, args) => {
		currentPromise = _applyPromised(fn, _this, args);
		currentPromise.finally(() => {
			currentPromise = null;
			if (options.trailing && trailingArgs && !timeout) {
				const promise = applyFn(_this, trailingArgs);
				trailingArgs = null;
				return promise;
			}
		});
		return currentPromise;
	};
	const debounced = function(...args) {
		if (options.trailing) trailingArgs = args;
		if (currentPromise) return currentPromise;
		return new Promise((resolve) => {
			const shouldCallNow = !timeout && options.leading;
			clearTimeout(timeout);
			timeout = setTimeout(() => {
				timeout = null;
				const promise = options.leading ? leadingValue : applyFn(this, args);
				trailingArgs = null;
				for (const _resolve of resolveList) _resolve(promise);
				resolveList = [];
			}, wait);
			if (shouldCallNow) {
				leadingValue = applyFn(this, args);
				resolve(leadingValue);
			} else resolveList.push(resolve);
		});
	};
	const _clearTimeout = (timer) => {
		if (timer) {
			clearTimeout(timer);
			timeout = null;
		}
	};
	debounced.isPending = () => !!timeout;
	debounced.cancel = () => {
		_clearTimeout(timeout);
		resolveList = [];
		trailingArgs = null;
	};
	debounced.flush = () => {
		_clearTimeout(timeout);
		if (!trailingArgs || currentPromise) return;
		const args = trailingArgs;
		trailingArgs = null;
		return applyFn(this, args);
	};
	return debounced;
}
async function _applyPromised(fn, _this, args) {
	return await fn.apply(_this, args);
}

if (!globalThis.$fetch) {
  globalThis.$fetch = $fetch$1.create({
    baseURL: baseURL()
  });
}
if (!("global" in globalThis)) {
  globalThis.global = globalThis;
}
const nuxtLinkDefaults = { "componentName": "NuxtLink" };
const asyncDataDefaults = { "value": null, "errorValue": null, "deep": true };
const appId = "nuxt-app";
function getNuxtAppCtx(id = appId) {
  return getContext(id, {
    asyncContext: false
  });
}
const NuxtPluginIndicator = "__nuxt_plugin";
function createNuxtApp(options) {
  let hydratingCount = 0;
  const nuxtApp = {
    _id: options.id || appId || "nuxt-app",
    _scope: effectScope(),
    provide: void 0,
    globalName: "nuxt",
    versions: {
      get nuxt() {
        return "3.19.3";
      },
      get vue() {
        return nuxtApp.vueApp.version;
      }
    },
    payload: shallowReactive({
      ...options.ssrContext?.payload || {},
      data: shallowReactive({}),
      state: reactive({}),
      once: /* @__PURE__ */ new Set(),
      _errors: shallowReactive({})
    }),
    static: {
      data: {}
    },
    runWithContext(fn) {
      if (nuxtApp._scope.active && !getCurrentScope()) {
        return nuxtApp._scope.run(() => callWithNuxt(nuxtApp, fn));
      }
      return callWithNuxt(nuxtApp, fn);
    },
    isHydrating: false,
    deferHydration() {
      if (!nuxtApp.isHydrating) {
        return () => {
        };
      }
      hydratingCount++;
      let called = false;
      return () => {
        if (called) {
          return;
        }
        called = true;
        hydratingCount--;
        if (hydratingCount === 0) {
          nuxtApp.isHydrating = false;
          return nuxtApp.callHook("app:suspense:resolve");
        }
      };
    },
    _asyncDataPromises: {},
    _asyncData: shallowReactive({}),
    _payloadRevivers: {},
    ...options
  };
  {
    nuxtApp.payload.serverRendered = true;
  }
  if (nuxtApp.ssrContext) {
    nuxtApp.payload.path = nuxtApp.ssrContext.url;
    nuxtApp.ssrContext.nuxt = nuxtApp;
    nuxtApp.ssrContext.payload = nuxtApp.payload;
    nuxtApp.ssrContext.config = {
      public: nuxtApp.ssrContext.runtimeConfig.public,
      app: nuxtApp.ssrContext.runtimeConfig.app
    };
  }
  nuxtApp.hooks = createHooks();
  nuxtApp.hook = nuxtApp.hooks.hook;
  {
    const contextCaller = async function(hooks, args) {
      for (const hook of hooks) {
        await nuxtApp.runWithContext(() => hook(...args));
      }
    };
    nuxtApp.hooks.callHook = (name, ...args) => nuxtApp.hooks.callHookWith(contextCaller, name, ...args);
  }
  nuxtApp.callHook = nuxtApp.hooks.callHook;
  nuxtApp.provide = (name, value) => {
    const $name = "$" + name;
    defineGetter(nuxtApp, $name, value);
    defineGetter(nuxtApp.vueApp.config.globalProperties, $name, value);
  };
  defineGetter(nuxtApp.vueApp, "$nuxt", nuxtApp);
  defineGetter(nuxtApp.vueApp.config.globalProperties, "$nuxt", nuxtApp);
  const runtimeConfig = options.ssrContext.runtimeConfig;
  nuxtApp.provide("config", runtimeConfig);
  return nuxtApp;
}
function registerPluginHooks(nuxtApp, plugin2) {
  if (plugin2.hooks) {
    nuxtApp.hooks.addHooks(plugin2.hooks);
  }
}
async function applyPlugin(nuxtApp, plugin2) {
  if (typeof plugin2 === "function") {
    const { provide: provide2 } = await nuxtApp.runWithContext(() => plugin2(nuxtApp)) || {};
    if (provide2 && typeof provide2 === "object") {
      for (const key in provide2) {
        nuxtApp.provide(key, provide2[key]);
      }
    }
  }
}
async function applyPlugins(nuxtApp, plugins2) {
  const resolvedPlugins = /* @__PURE__ */ new Set();
  const unresolvedPlugins = [];
  const parallels = [];
  let error = void 0;
  let promiseDepth = 0;
  async function executePlugin(plugin2) {
    const unresolvedPluginsForThisPlugin = plugin2.dependsOn?.filter((name) => plugins2.some((p) => p._name === name) && !resolvedPlugins.has(name)) ?? [];
    if (unresolvedPluginsForThisPlugin.length > 0) {
      unresolvedPlugins.push([new Set(unresolvedPluginsForThisPlugin), plugin2]);
    } else {
      const promise = applyPlugin(nuxtApp, plugin2).then(async () => {
        if (plugin2._name) {
          resolvedPlugins.add(plugin2._name);
          await Promise.all(unresolvedPlugins.map(async ([dependsOn, unexecutedPlugin]) => {
            if (dependsOn.has(plugin2._name)) {
              dependsOn.delete(plugin2._name);
              if (dependsOn.size === 0) {
                promiseDepth++;
                await executePlugin(unexecutedPlugin);
              }
            }
          }));
        }
      }).catch((e) => {
        if (!plugin2.parallel && !nuxtApp.payload.error) {
          throw e;
        }
        error ||= e;
      });
      if (plugin2.parallel) {
        parallels.push(promise);
      } else {
        await promise;
      }
    }
  }
  for (const plugin2 of plugins2) {
    if (nuxtApp.ssrContext?.islandContext && plugin2.env?.islands === false) {
      continue;
    }
    registerPluginHooks(nuxtApp, plugin2);
  }
  for (const plugin2 of plugins2) {
    if (nuxtApp.ssrContext?.islandContext && plugin2.env?.islands === false) {
      continue;
    }
    await executePlugin(plugin2);
  }
  await Promise.all(parallels);
  if (promiseDepth) {
    for (let i = 0; i < promiseDepth; i++) {
      await Promise.all(parallels);
    }
  }
  if (error) {
    throw nuxtApp.payload.error || error;
  }
}
// @__NO_SIDE_EFFECTS__
function defineNuxtPlugin(plugin2) {
  if (typeof plugin2 === "function") {
    return plugin2;
  }
  const _name = plugin2._name || plugin2.name;
  delete plugin2.name;
  return Object.assign(plugin2.setup || (() => {
  }), plugin2, { [NuxtPluginIndicator]: true, _name });
}
function callWithNuxt(nuxt, setup, args) {
  const fn = () => setup();
  const nuxtAppCtx = getNuxtAppCtx(nuxt._id);
  {
    return nuxt.vueApp.runWithContext(() => nuxtAppCtx.callAsync(nuxt, fn));
  }
}
function tryUseNuxtApp(id) {
  let nuxtAppInstance;
  if (hasInjectionContext()) {
    nuxtAppInstance = getCurrentInstance()?.appContext.app.$nuxt;
  }
  nuxtAppInstance ||= getNuxtAppCtx(id).tryUse();
  return nuxtAppInstance || null;
}
function useNuxtApp(id) {
  const nuxtAppInstance = tryUseNuxtApp(id);
  if (!nuxtAppInstance) {
    {
      throw new Error("[nuxt] instance unavailable");
    }
  }
  return nuxtAppInstance;
}
// @__NO_SIDE_EFFECTS__
function useRuntimeConfig(_event) {
  return useNuxtApp().$config;
}
function defineGetter(obj, key, val) {
  Object.defineProperty(obj, key, { get: () => val });
}
const PageRouteSymbol = Symbol("route");
globalThis._importMeta_.url.replace(/\/app\/.*$/, "/");
const useRouter = () => {
  return useNuxtApp()?.$router;
};
const useRoute = () => {
  if (hasInjectionContext()) {
    return inject(PageRouteSymbol, useNuxtApp()._route);
  }
  return useNuxtApp()._route;
};
// @__NO_SIDE_EFFECTS__
function defineNuxtRouteMiddleware(middleware) {
  return middleware;
}
const isProcessingMiddleware = () => {
  try {
    if (useNuxtApp()._processingMiddleware) {
      return true;
    }
  } catch {
    return false;
  }
  return false;
};
const URL_QUOTE_RE = /"/g;
const navigateTo = (to, options) => {
  to ||= "/";
  const toPath = typeof to === "string" ? to : "path" in to ? resolveRouteObject(to) : useRouter().resolve(to).href;
  const isExternalHost = hasProtocol(toPath, { acceptRelative: true });
  const isExternal = options?.external || isExternalHost;
  if (isExternal) {
    if (!options?.external) {
      throw new Error("Navigating to an external URL is not allowed by default. Use `navigateTo(url, { external: true })`.");
    }
    const { protocol } = new URL(toPath, "http://localhost");
    if (protocol && isScriptProtocol(protocol)) {
      throw new Error(`Cannot navigate to a URL with '${protocol}' protocol.`);
    }
  }
  const inMiddleware = isProcessingMiddleware();
  const router = useRouter();
  const nuxtApp = useNuxtApp();
  {
    if (nuxtApp.ssrContext) {
      const fullPath = typeof to === "string" || isExternal ? toPath : router.resolve(to).fullPath || "/";
      const location2 = isExternal ? toPath : joinURL((/* @__PURE__ */ useRuntimeConfig()).app.baseURL, fullPath);
      const redirect = async function(response) {
        await nuxtApp.callHook("app:redirected");
        const encodedLoc = location2.replace(URL_QUOTE_RE, "%22");
        const encodedHeader = encodeURL(location2, isExternalHost);
        nuxtApp.ssrContext._renderResponse = {
          statusCode: sanitizeStatusCode(options?.redirectCode || 302, 302),
          body: `<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0; url=${encodedLoc}"></head></html>`,
          headers: { location: encodedHeader }
        };
        return response;
      };
      if (!isExternal && inMiddleware) {
        router.afterEach((final) => final.fullPath === fullPath ? redirect(false) : void 0);
        return to;
      }
      return redirect(!inMiddleware ? void 0 : (
        /* abort route navigation */
        false
      ));
    }
  }
  if (isExternal) {
    nuxtApp._scope.stop();
    if (options?.replace) {
      (void 0).replace(toPath);
    } else {
      (void 0).href = toPath;
    }
    if (inMiddleware) {
      if (!nuxtApp.isHydrating) {
        return false;
      }
      return new Promise(() => {
      });
    }
    return Promise.resolve();
  }
  return options?.replace ? router.replace(to) : router.push(to);
};
function resolveRouteObject(to) {
  return withQuery(to.path || "", to.query || {}) + (to.hash || "");
}
function encodeURL(location2, isExternalHost = false) {
  const url = new URL(location2, "http://localhost");
  if (!isExternalHost) {
    return url.pathname + url.search + url.hash;
  }
  if (location2.startsWith("//")) {
    return url.toString().replace(url.protocol, "");
  }
  return url.toString();
}
const NUXT_ERROR_SIGNATURE = "__nuxt_error";
const useError = /* @__NO_SIDE_EFFECTS__ */ () => toRef(useNuxtApp().payload, "error");
const showError = (error) => {
  const nuxtError = createError(error);
  try {
    const error2 = /* @__PURE__ */ useError();
    if (false) ;
    error2.value ||= nuxtError;
  } catch {
    throw nuxtError;
  }
  return nuxtError;
};
const isNuxtError = (error) => !!error && typeof error === "object" && NUXT_ERROR_SIGNATURE in error;
const createError = (error) => {
  const nuxtError = createError$1(error);
  Object.defineProperty(nuxtError, NUXT_ERROR_SIGNATURE, {
    value: true,
    configurable: false,
    writable: false
  });
  return nuxtError;
};
const unhead_k2P3m_ZDyjlr2mMYnoDPwavjsDN8hBlk9cFai0bbopU = /* @__PURE__ */ defineNuxtPlugin({
  name: "nuxt:head",
  enforce: "pre",
  setup(nuxtApp) {
    const head = nuxtApp.ssrContext.head;
    nuxtApp.vueApp.use(head);
  }
});
async function getRouteRules(arg) {
  const path = typeof arg === "string" ? arg : arg.path;
  {
    useNuxtApp().ssrContext._preloadManifest = true;
    const _routeRulesMatcher = toRouteMatcher(
      createRouter({ routes: (/* @__PURE__ */ useRuntimeConfig()).nitro.routeRules })
    );
    return defu({}, ..._routeRulesMatcher.matchAll(path).reverse());
  }
}
const manifest_45route_45rule = /* @__PURE__ */ defineNuxtRouteMiddleware(async (to) => {
  {
    return;
  }
});
const globalMiddleware = [
  manifest_45route_45rule
];
function getRouteFromPath(fullPath) {
  const route = fullPath && typeof fullPath === "object" ? fullPath : {};
  if (typeof fullPath === "object") {
    fullPath = stringifyParsedURL({
      pathname: fullPath.path || "",
      search: stringifyQuery(fullPath.query || {}),
      hash: fullPath.hash || ""
    });
  }
  const url = new URL(fullPath.toString(), "http://localhost");
  return {
    path: url.pathname,
    fullPath,
    query: parseQuery(url.search),
    hash: url.hash,
    // stub properties for compat with vue-router
    params: route.params || {},
    name: void 0,
    matched: route.matched || [],
    redirectedFrom: void 0,
    meta: route.meta || {},
    href: fullPath
  };
}
const router_DclsWNDeVV7SyG4lslgLnjbQUK1ws8wgf2FHaAbo7Cw = /* @__PURE__ */ defineNuxtPlugin({
  name: "nuxt:router",
  enforce: "pre",
  setup(nuxtApp) {
    const initialURL = nuxtApp.ssrContext.url;
    const routes = [];
    const hooks = {
      "navigate:before": [],
      "resolve:before": [],
      "navigate:after": [],
      "error": []
    };
    const registerHook = (hook, guard) => {
      hooks[hook].push(guard);
      return () => hooks[hook].splice(hooks[hook].indexOf(guard), 1);
    };
    (/* @__PURE__ */ useRuntimeConfig()).app.baseURL;
    const route = reactive(getRouteFromPath(initialURL));
    async function handleNavigation(url, replace) {
      try {
        const to = getRouteFromPath(url);
        for (const middleware of hooks["navigate:before"]) {
          const result = await middleware(to, route);
          if (result === false || result instanceof Error) {
            return;
          }
          if (typeof result === "string" && result.length) {
            return handleNavigation(result, true);
          }
        }
        for (const handler of hooks["resolve:before"]) {
          await handler(to, route);
        }
        Object.assign(route, to);
        if (false) ;
        for (const middleware of hooks["navigate:after"]) {
          await middleware(to, route);
        }
      } catch (err) {
        for (const handler of hooks.error) {
          await handler(err);
        }
      }
    }
    const currentRoute = computed(() => route);
    const router = {
      currentRoute,
      isReady: () => Promise.resolve(),
      // These options provide a similar API to vue-router but have no effect
      options: {},
      install: () => Promise.resolve(),
      // Navigation
      push: (url) => handleNavigation(url),
      replace: (url) => handleNavigation(url),
      back: () => (void 0).history.go(-1),
      go: (delta) => (void 0).history.go(delta),
      forward: () => (void 0).history.go(1),
      // Guards
      beforeResolve: (guard) => registerHook("resolve:before", guard),
      beforeEach: (guard) => registerHook("navigate:before", guard),
      afterEach: (guard) => registerHook("navigate:after", guard),
      onError: (handler) => registerHook("error", handler),
      // Routes
      resolve: getRouteFromPath,
      addRoute: (parentName, route2) => {
        routes.push(route2);
      },
      getRoutes: () => routes,
      hasRoute: (name) => routes.some((route2) => route2.name === name),
      removeRoute: (name) => {
        const index2 = routes.findIndex((route2) => route2.name === name);
        if (index2 !== -1) {
          routes.splice(index2, 1);
        }
      }
    };
    nuxtApp.vueApp.component("RouterLink", defineComponent({
      functional: true,
      props: {
        to: {
          type: String,
          required: true
        },
        custom: Boolean,
        replace: Boolean,
        // Not implemented
        activeClass: String,
        exactActiveClass: String,
        ariaCurrentValue: String
      },
      setup: (props, { slots }) => {
        const navigate = () => handleNavigation(props.to, props.replace);
        return () => {
          const route2 = router.resolve(props.to);
          return props.custom ? slots.default?.({ href: props.to, navigate, route: route2 }) : h("a", { href: props.to, onClick: (e) => {
            e.preventDefault();
            return navigate();
          } }, slots);
        };
      }
    }));
    nuxtApp._route = route;
    nuxtApp._middleware ||= {
      global: [],
      named: {}
    };
    const initialLayout = nuxtApp.payload.state._layout;
    nuxtApp.hooks.hookOnce("app:created", async () => {
      router.beforeEach(async (to, from) => {
        to.meta = reactive(to.meta || {});
        if (nuxtApp.isHydrating && initialLayout && !isReadonly(to.meta.layout)) {
          to.meta.layout = initialLayout;
        }
        nuxtApp._processingMiddleware = true;
        if (!nuxtApp.ssrContext?.islandContext) {
          const middlewareEntries = /* @__PURE__ */ new Set([...globalMiddleware, ...nuxtApp._middleware.global]);
          {
            const routeRules = await nuxtApp.runWithContext(() => getRouteRules({ path: to.path }));
            if (routeRules.appMiddleware) {
              for (const key in routeRules.appMiddleware) {
                const guard = nuxtApp._middleware.named[key];
                if (!guard) {
                  return;
                }
                if (routeRules.appMiddleware[key]) {
                  middlewareEntries.add(guard);
                } else {
                  middlewareEntries.delete(guard);
                }
              }
            }
          }
          for (const middleware of middlewareEntries) {
            const result = await nuxtApp.runWithContext(() => middleware(to, from));
            {
              if (result === false || result instanceof Error) {
                const error = result || createError$1({
                  statusCode: 404,
                  statusMessage: `Page Not Found: ${initialURL}`,
                  data: {
                    path: initialURL
                  }
                });
                delete nuxtApp._processingMiddleware;
                return nuxtApp.runWithContext(() => showError(error));
              }
            }
            if (result === true) {
              continue;
            }
            if (result || result === false) {
              return result;
            }
          }
        }
      });
      router.afterEach(() => {
        delete nuxtApp._processingMiddleware;
      });
      await router.replace(initialURL);
      if (!isEqual(route.fullPath, initialURL)) {
        await nuxtApp.runWithContext(() => navigateTo(route.fullPath));
      }
    });
    return {
      provide: {
        route,
        router
      }
    };
  }
});
function injectHead(nuxtApp) {
  const nuxt = nuxtApp || tryUseNuxtApp();
  return nuxt?.ssrContext?.head || nuxt?.runWithContext(() => {
    if (hasInjectionContext()) {
      return inject(headSymbol);
    }
  });
}
function useHead(input, options = {}) {
  const head = injectHead(options.nuxt);
  if (head) {
    return useHead$1(input, { head, ...options });
  }
}
function useSeoMeta(input, options = {}) {
  const head = injectHead(options.nuxt);
  if (head) {
    return useSeoMeta$1(input, { head, ...options });
  }
}
function definePayloadReducer(name, reduce) {
  {
    useNuxtApp().ssrContext._payloadReducers[name] = reduce;
  }
}
const reducers = [
  ["NuxtError", (data) => isNuxtError(data) && data.toJSON()],
  ["EmptyShallowRef", (data) => isRef(data) && isShallow(data) && !data.value && (typeof data.value === "bigint" ? "0n" : JSON.stringify(data.value) || "_")],
  ["EmptyRef", (data) => isRef(data) && !data.value && (typeof data.value === "bigint" ? "0n" : JSON.stringify(data.value) || "_")],
  ["ShallowRef", (data) => isRef(data) && isShallow(data) && data.value],
  ["ShallowReactive", (data) => isReactive(data) && isShallow(data) && toRaw(data)],
  ["Ref", (data) => isRef(data) && data.value],
  ["Reactive", (data) => isReactive(data) && toRaw(data)]
];
const revive_payload_server_MVtmlZaQpj6ApFmshWfUWl5PehCebzaBf2NuRMiIbms = /* @__PURE__ */ defineNuxtPlugin({
  name: "nuxt:revive-payload:server",
  setup() {
    for (const [reducer, fn] of reducers) {
      definePayloadReducer(reducer, fn);
    }
  }
});
/*!
 * pinia v2.3.1
 * (c) 2025 Eduardo San Martin Morote
 * @license MIT
 */
let activePinia;
const setActivePinia = (pinia) => activePinia = pinia;
const piniaSymbol = (
  /* istanbul ignore next */
  Symbol()
);
function isPlainObject(o) {
  return o && typeof o === "object" && Object.prototype.toString.call(o) === "[object Object]" && typeof o.toJSON !== "function";
}
var MutationType;
(function(MutationType2) {
  MutationType2["direct"] = "direct";
  MutationType2["patchObject"] = "patch object";
  MutationType2["patchFunction"] = "patch function";
})(MutationType || (MutationType = {}));
function createPinia() {
  const scope = effectScope(true);
  const state = scope.run(() => ref({}));
  let _p = [];
  let toBeInstalled = [];
  const pinia = markRaw({
    install(app) {
      setActivePinia(pinia);
      {
        pinia._a = app;
        app.provide(piniaSymbol, pinia);
        app.config.globalProperties.$pinia = pinia;
        toBeInstalled.forEach((plugin2) => _p.push(plugin2));
        toBeInstalled = [];
      }
    },
    use(plugin2) {
      if (!this._a && true) {
        toBeInstalled.push(plugin2);
      } else {
        _p.push(plugin2);
      }
      return this;
    },
    _p,
    // it's actually undefined here
    // @ts-expect-error
    _a: null,
    _e: scope,
    _s: /* @__PURE__ */ new Map(),
    state
  });
  return pinia;
}
const noop = () => {
};
function addSubscription(subscriptions, callback, detached, onCleanup = noop) {
  subscriptions.push(callback);
  const removeSubscription = () => {
    const idx = subscriptions.indexOf(callback);
    if (idx > -1) {
      subscriptions.splice(idx, 1);
      onCleanup();
    }
  };
  if (!detached && getCurrentScope()) {
    onScopeDispose(removeSubscription);
  }
  return removeSubscription;
}
function triggerSubscriptions(subscriptions, ...args) {
  subscriptions.slice().forEach((callback) => {
    callback(...args);
  });
}
const fallbackRunWithContext = (fn) => fn();
const ACTION_MARKER = Symbol();
const ACTION_NAME = Symbol();
function mergeReactiveObjects(target, patchToApply) {
  if (target instanceof Map && patchToApply instanceof Map) {
    patchToApply.forEach((value, key) => target.set(key, value));
  } else if (target instanceof Set && patchToApply instanceof Set) {
    patchToApply.forEach(target.add, target);
  }
  for (const key in patchToApply) {
    if (!patchToApply.hasOwnProperty(key))
      continue;
    const subPatch = patchToApply[key];
    const targetValue = target[key];
    if (isPlainObject(targetValue) && isPlainObject(subPatch) && target.hasOwnProperty(key) && !isRef(subPatch) && !isReactive(subPatch)) {
      target[key] = mergeReactiveObjects(targetValue, subPatch);
    } else {
      target[key] = subPatch;
    }
  }
  return target;
}
const skipHydrateSymbol = (
  /* istanbul ignore next */
  Symbol()
);
function shouldHydrate(obj) {
  return !isPlainObject(obj) || !obj.hasOwnProperty(skipHydrateSymbol);
}
const { assign } = Object;
function isComputed(o) {
  return !!(isRef(o) && o.effect);
}
function createOptionsStore(id, options, pinia, hot) {
  const { state, actions, getters } = options;
  const initialState = pinia.state.value[id];
  let store;
  function setup() {
    if (!initialState && (true)) {
      {
        pinia.state.value[id] = state ? state() : {};
      }
    }
    const localState = toRefs(pinia.state.value[id]);
    return assign(localState, actions, Object.keys(getters || {}).reduce((computedGetters, name) => {
      computedGetters[name] = markRaw(computed(() => {
        setActivePinia(pinia);
        const store2 = pinia._s.get(id);
        return getters[name].call(store2, store2);
      }));
      return computedGetters;
    }, {}));
  }
  store = createSetupStore(id, setup, options, pinia, hot, true);
  return store;
}
function createSetupStore($id, setup, options = {}, pinia, hot, isOptionsStore) {
  let scope;
  const optionsForPlugin = assign({ actions: {} }, options);
  const $subscribeOptions = { deep: true };
  let isListening;
  let isSyncListening;
  let subscriptions = [];
  let actionSubscriptions = [];
  let debuggerEvents;
  const initialState = pinia.state.value[$id];
  if (!isOptionsStore && !initialState && (true)) {
    {
      pinia.state.value[$id] = {};
    }
  }
  ref({});
  let activeListener;
  function $patch(partialStateOrMutator) {
    let subscriptionMutation;
    isListening = isSyncListening = false;
    if (typeof partialStateOrMutator === "function") {
      partialStateOrMutator(pinia.state.value[$id]);
      subscriptionMutation = {
        type: MutationType.patchFunction,
        storeId: $id,
        events: debuggerEvents
      };
    } else {
      mergeReactiveObjects(pinia.state.value[$id], partialStateOrMutator);
      subscriptionMutation = {
        type: MutationType.patchObject,
        payload: partialStateOrMutator,
        storeId: $id,
        events: debuggerEvents
      };
    }
    const myListenerId = activeListener = Symbol();
    nextTick().then(() => {
      if (activeListener === myListenerId) {
        isListening = true;
      }
    });
    isSyncListening = true;
    triggerSubscriptions(subscriptions, subscriptionMutation, pinia.state.value[$id]);
  }
  const $reset = isOptionsStore ? function $reset2() {
    const { state } = options;
    const newState = state ? state() : {};
    this.$patch(($state) => {
      assign($state, newState);
    });
  } : (
    /* istanbul ignore next */
    noop
  );
  function $dispose() {
    scope.stop();
    subscriptions = [];
    actionSubscriptions = [];
    pinia._s.delete($id);
  }
  const action = (fn, name = "") => {
    if (ACTION_MARKER in fn) {
      fn[ACTION_NAME] = name;
      return fn;
    }
    const wrappedAction = function() {
      setActivePinia(pinia);
      const args = Array.from(arguments);
      const afterCallbackList = [];
      const onErrorCallbackList = [];
      function after(callback) {
        afterCallbackList.push(callback);
      }
      function onError(callback) {
        onErrorCallbackList.push(callback);
      }
      triggerSubscriptions(actionSubscriptions, {
        args,
        name: wrappedAction[ACTION_NAME],
        store,
        after,
        onError
      });
      let ret;
      try {
        ret = fn.apply(this && this.$id === $id ? this : store, args);
      } catch (error) {
        triggerSubscriptions(onErrorCallbackList, error);
        throw error;
      }
      if (ret instanceof Promise) {
        return ret.then((value) => {
          triggerSubscriptions(afterCallbackList, value);
          return value;
        }).catch((error) => {
          triggerSubscriptions(onErrorCallbackList, error);
          return Promise.reject(error);
        });
      }
      triggerSubscriptions(afterCallbackList, ret);
      return ret;
    };
    wrappedAction[ACTION_MARKER] = true;
    wrappedAction[ACTION_NAME] = name;
    return wrappedAction;
  };
  const partialStore = {
    _p: pinia,
    // _s: scope,
    $id,
    $onAction: addSubscription.bind(null, actionSubscriptions),
    $patch,
    $reset,
    $subscribe(callback, options2 = {}) {
      const removeSubscription = addSubscription(subscriptions, callback, options2.detached, () => stopWatcher());
      const stopWatcher = scope.run(() => watch(() => pinia.state.value[$id], (state) => {
        if (options2.flush === "sync" ? isSyncListening : isListening) {
          callback({
            storeId: $id,
            type: MutationType.direct,
            events: debuggerEvents
          }, state);
        }
      }, assign({}, $subscribeOptions, options2)));
      return removeSubscription;
    },
    $dispose
  };
  const store = reactive(partialStore);
  pinia._s.set($id, store);
  const runWithContext = pinia._a && pinia._a.runWithContext || fallbackRunWithContext;
  const setupStore = runWithContext(() => pinia._e.run(() => (scope = effectScope()).run(() => setup({ action }))));
  for (const key in setupStore) {
    const prop = setupStore[key];
    if (isRef(prop) && !isComputed(prop) || isReactive(prop)) {
      if (!isOptionsStore) {
        if (initialState && shouldHydrate(prop)) {
          if (isRef(prop)) {
            prop.value = initialState[key];
          } else {
            mergeReactiveObjects(prop, initialState[key]);
          }
        }
        {
          pinia.state.value[$id][key] = prop;
        }
      }
    } else if (typeof prop === "function") {
      const actionValue = action(prop, key);
      {
        setupStore[key] = actionValue;
      }
      optionsForPlugin.actions[key] = prop;
    } else ;
  }
  {
    assign(store, setupStore);
    assign(toRaw(store), setupStore);
  }
  Object.defineProperty(store, "$state", {
    get: () => pinia.state.value[$id],
    set: (state) => {
      $patch(($state) => {
        assign($state, state);
      });
    }
  });
  pinia._p.forEach((extender) => {
    {
      assign(store, scope.run(() => extender({
        store,
        app: pinia._a,
        pinia,
        options: optionsForPlugin
      })));
    }
  });
  if (initialState && isOptionsStore && options.hydrate) {
    options.hydrate(store.$state, initialState);
  }
  isListening = true;
  isSyncListening = true;
  return store;
}
/*! #__NO_SIDE_EFFECTS__ */
// @__NO_SIDE_EFFECTS__
function defineStore(idOrOptions, setup, setupOptions) {
  let id;
  let options;
  const isSetupStore = typeof setup === "function";
  if (typeof idOrOptions === "string") {
    id = idOrOptions;
    options = isSetupStore ? setupOptions : setup;
  } else {
    options = idOrOptions;
    id = idOrOptions.id;
  }
  function useStore(pinia, hot) {
    const hasContext = hasInjectionContext();
    pinia = // in test mode, ignore the argument provided as we can always retrieve a
    // pinia instance with getActivePinia()
    (pinia) || (hasContext ? inject(piniaSymbol, null) : null);
    if (pinia)
      setActivePinia(pinia);
    pinia = activePinia;
    if (!pinia._s.has(id)) {
      if (isSetupStore) {
        createSetupStore(id, setup, options, pinia);
      } else {
        createOptionsStore(id, options, pinia);
      }
    }
    const store = pinia._s.get(id);
    return store;
  }
  useStore.$id = id;
  return useStore;
}
defineComponent({
  name: "ServerPlaceholder",
  render() {
    return createElementBlock("div");
  }
});
const clientOnlySymbol = Symbol.for("nuxt:client-only");
defineComponent({
  name: "ClientOnly",
  inheritAttrs: false,
  props: ["fallback", "placeholder", "placeholderTag", "fallbackTag"],
  ...false,
  setup(props, { slots, attrs }) {
    const mounted = shallowRef(false);
    const vm = getCurrentInstance();
    if (vm) {
      vm._nuxtClientOnly = true;
    }
    provide(clientOnlySymbol, true);
    return () => {
      if (mounted.value) {
        const vnodes = slots.default?.();
        if (vnodes && vnodes.length === 1) {
          return [cloneVNode(vnodes[0], attrs)];
        }
        return vnodes;
      }
      const slot = slots.fallback || slots.placeholder;
      if (slot) {
        return h(slot);
      }
      const fallbackStr = props.fallback || props.placeholder || "";
      const fallbackTag = props.fallbackTag || props.placeholderTag || "span";
      return createElementBlock(fallbackTag, attrs, fallbackStr);
    };
  }
});
const isDefer = (dedupe) => dedupe === "defer" || dedupe === false;
function useAsyncData(...args) {
  const autoKey = typeof args[args.length - 1] === "string" ? args.pop() : void 0;
  if (_isAutoKeyNeeded(args[0], args[1])) {
    args.unshift(autoKey);
  }
  let [_key, _handler, options = {}] = args;
  const key = computed(() => toValue(_key));
  if (typeof key.value !== "string") {
    throw new TypeError("[nuxt] [useAsyncData] key must be a string.");
  }
  if (typeof _handler !== "function") {
    throw new TypeError("[nuxt] [useAsyncData] handler must be a function.");
  }
  const nuxtApp = useNuxtApp();
  options.server ??= true;
  options.default ??= getDefault;
  options.getCachedData ??= getDefaultCachedData;
  options.lazy ??= false;
  options.immediate ??= true;
  options.deep ??= asyncDataDefaults.deep;
  options.dedupe ??= "cancel";
  options._functionName || "useAsyncData";
  nuxtApp._asyncData[key.value];
  function createInitialFetch() {
    const initialFetchOptions = { cause: "initial", dedupe: options.dedupe };
    if (!nuxtApp._asyncData[key.value]?._init) {
      initialFetchOptions.cachedData = options.getCachedData(key.value, nuxtApp, { cause: "initial" });
      nuxtApp._asyncData[key.value] = createAsyncData(nuxtApp, key.value, _handler, options, initialFetchOptions.cachedData);
    }
    return () => nuxtApp._asyncData[key.value].execute(initialFetchOptions);
  }
  const initialFetch = createInitialFetch();
  const asyncData = nuxtApp._asyncData[key.value];
  asyncData._deps++;
  const fetchOnServer = options.server !== false && nuxtApp.payload.serverRendered;
  if (fetchOnServer && options.immediate) {
    const promise = initialFetch();
    if (getCurrentInstance()) {
      onServerPrefetch(() => promise);
    } else {
      nuxtApp.hook("app:created", async () => {
        await promise;
      });
    }
  }
  const asyncReturn = {
    data: writableComputedRef(() => nuxtApp._asyncData[key.value]?.data),
    pending: writableComputedRef(() => nuxtApp._asyncData[key.value]?.pending),
    status: writableComputedRef(() => nuxtApp._asyncData[key.value]?.status),
    error: writableComputedRef(() => nuxtApp._asyncData[key.value]?.error),
    refresh: (...args2) => {
      if (!nuxtApp._asyncData[key.value]?._init) {
        const initialFetch2 = createInitialFetch();
        return initialFetch2();
      }
      return nuxtApp._asyncData[key.value].execute(...args2);
    },
    execute: (...args2) => asyncReturn.refresh(...args2),
    clear: () => clearNuxtDataByKey(nuxtApp, key.value)
  };
  const asyncDataPromise = Promise.resolve(nuxtApp._asyncDataPromises[key.value]).then(() => asyncReturn);
  Object.assign(asyncDataPromise, asyncReturn);
  return asyncDataPromise;
}
function writableComputedRef(getter) {
  return computed({
    get() {
      return getter()?.value;
    },
    set(value) {
      const ref2 = getter();
      if (ref2) {
        ref2.value = value;
      }
    }
  });
}
function _isAutoKeyNeeded(keyOrFetcher, fetcher) {
  if (typeof keyOrFetcher === "string") {
    return false;
  }
  if (typeof keyOrFetcher === "object" && keyOrFetcher !== null) {
    return false;
  }
  if (typeof keyOrFetcher === "function" && typeof fetcher === "function") {
    return false;
  }
  return true;
}
function clearNuxtDataByKey(nuxtApp, key) {
  if (key in nuxtApp.payload.data) {
    nuxtApp.payload.data[key] = void 0;
  }
  if (key in nuxtApp.payload._errors) {
    nuxtApp.payload._errors[key] = asyncDataDefaults.errorValue;
  }
  if (nuxtApp._asyncData[key]) {
    nuxtApp._asyncData[key].data.value = void 0;
    nuxtApp._asyncData[key].error.value = asyncDataDefaults.errorValue;
    {
      nuxtApp._asyncData[key].pending.value = false;
    }
    nuxtApp._asyncData[key].status.value = "idle";
  }
  if (key in nuxtApp._asyncDataPromises) {
    if (nuxtApp._asyncDataPromises[key]) {
      nuxtApp._asyncDataPromises[key].cancelled = true;
    }
    nuxtApp._asyncDataPromises[key] = void 0;
  }
}
function pick(obj, keys) {
  const newObj = {};
  for (const key of keys) {
    newObj[key] = obj[key];
  }
  return newObj;
}
function createAsyncData(nuxtApp, key, _handler, options, initialCachedData) {
  nuxtApp.payload._errors[key] ??= asyncDataDefaults.errorValue;
  const hasCustomGetCachedData = options.getCachedData !== getDefaultCachedData;
  const handler = _handler ;
  const _ref = options.deep ? ref : shallowRef;
  const hasCachedData = initialCachedData != null;
  const unsubRefreshAsyncData = nuxtApp.hook("app:data:refresh", async (keys) => {
    if (!keys || keys.includes(key)) {
      await asyncData.execute({ cause: "refresh:hook" });
    }
  });
  const asyncData = {
    data: _ref(hasCachedData ? initialCachedData : options.default()),
    pending: shallowRef(!hasCachedData),
    error: toRef(nuxtApp.payload._errors, key),
    status: shallowRef("idle"),
    execute: (...args) => {
      const [_opts, newValue = void 0] = args;
      const opts = _opts && newValue === void 0 && typeof _opts === "object" ? _opts : {};
      if (nuxtApp._asyncDataPromises[key]) {
        if (isDefer(opts.dedupe ?? options.dedupe)) {
          return nuxtApp._asyncDataPromises[key];
        }
        nuxtApp._asyncDataPromises[key].cancelled = true;
      }
      if (opts.cause === "initial" || nuxtApp.isHydrating) {
        const cachedData = "cachedData" in opts ? opts.cachedData : options.getCachedData(key, nuxtApp, { cause: opts.cause ?? "refresh:manual" });
        if (cachedData != null) {
          nuxtApp.payload.data[key] = asyncData.data.value = cachedData;
          asyncData.error.value = asyncDataDefaults.errorValue;
          asyncData.status.value = "success";
          return Promise.resolve(cachedData);
        }
      }
      {
        asyncData.pending.value = true;
      }
      asyncData.status.value = "pending";
      const promise = new Promise(
        (resolve, reject) => {
          try {
            resolve(handler(nuxtApp));
          } catch (err) {
            reject(err);
          }
        }
      ).then(async (_result) => {
        if (promise.cancelled) {
          return nuxtApp._asyncDataPromises[key];
        }
        let result = _result;
        if (options.transform) {
          result = await options.transform(_result);
        }
        if (options.pick) {
          result = pick(result, options.pick);
        }
        nuxtApp.payload.data[key] = result;
        asyncData.data.value = result;
        asyncData.error.value = asyncDataDefaults.errorValue;
        asyncData.status.value = "success";
      }).catch((error) => {
        if (promise.cancelled) {
          return nuxtApp._asyncDataPromises[key];
        }
        asyncData.error.value = createError(error);
        asyncData.data.value = unref(options.default());
        asyncData.status.value = "error";
      }).finally(() => {
        if (promise.cancelled) {
          return;
        }
        {
          asyncData.pending.value = false;
        }
        delete nuxtApp._asyncDataPromises[key];
      });
      nuxtApp._asyncDataPromises[key] = promise;
      return nuxtApp._asyncDataPromises[key];
    },
    _execute: debounce((...args) => asyncData.execute(...args), 0, { leading: true }),
    _default: options.default,
    _deps: 0,
    _init: true,
    _hash: void 0,
    _off: () => {
      unsubRefreshAsyncData();
      if (nuxtApp._asyncData[key]?._init) {
        nuxtApp._asyncData[key]._init = false;
      }
      if (!hasCustomGetCachedData) {
        nextTick(() => {
          if (!nuxtApp._asyncData[key]?._init) {
            clearNuxtDataByKey(nuxtApp, key);
            asyncData.execute = () => Promise.resolve();
            asyncData.data.value = asyncDataDefaults.value;
          }
        });
      }
    }
  };
  return asyncData;
}
const getDefault = () => asyncDataDefaults.value;
const getDefaultCachedData = (key, nuxtApp, ctx) => {
  if (nuxtApp.isHydrating) {
    return nuxtApp.payload.data[key];
  }
  if (ctx.cause !== "refresh:manual" && ctx.cause !== "refresh:hook") {
    return nuxtApp.static.data[key];
  }
};
const inlineConfig = {
  "nuxt": {},
  "icon": {
    "provider": "server",
    "class": "",
    "aliases": {},
    "iconifyApiEndpoint": "https://api.iconify.design",
    "localApiEndpoint": "/api/_nuxt_icon",
    "fallbackToApi": true,
    "cssSelectorPrefix": "i-",
    "cssWherePseudo": true,
    "mode": "css",
    "attrs": {
      "aria-hidden": true
    },
    "collections": [
      "academicons",
      "akar-icons",
      "ant-design",
      "arcticons",
      "basil",
      "bi",
      "bitcoin-icons",
      "bpmn",
      "brandico",
      "bx",
      "bxl",
      "bxs",
      "bytesize",
      "carbon",
      "catppuccin",
      "cbi",
      "charm",
      "ci",
      "cib",
      "cif",
      "cil",
      "circle-flags",
      "circum",
      "clarity",
      "codicon",
      "covid",
      "cryptocurrency",
      "cryptocurrency-color",
      "dashicons",
      "devicon",
      "devicon-plain",
      "ei",
      "el",
      "emojione",
      "emojione-monotone",
      "emojione-v1",
      "entypo",
      "entypo-social",
      "eos-icons",
      "ep",
      "et",
      "eva",
      "f7",
      "fa",
      "fa-brands",
      "fa-regular",
      "fa-solid",
      "fa6-brands",
      "fa6-regular",
      "fa6-solid",
      "fad",
      "fe",
      "feather",
      "file-icons",
      "flag",
      "flagpack",
      "flat-color-icons",
      "flat-ui",
      "flowbite",
      "fluent",
      "fluent-emoji",
      "fluent-emoji-flat",
      "fluent-emoji-high-contrast",
      "fluent-mdl2",
      "fontelico",
      "fontisto",
      "formkit",
      "foundation",
      "fxemoji",
      "gala",
      "game-icons",
      "geo",
      "gg",
      "gis",
      "gravity-ui",
      "gridicons",
      "grommet-icons",
      "guidance",
      "healthicons",
      "heroicons",
      "heroicons-outline",
      "heroicons-solid",
      "hugeicons",
      "humbleicons",
      "ic",
      "icomoon-free",
      "icon-park",
      "icon-park-outline",
      "icon-park-solid",
      "icon-park-twotone",
      "iconamoon",
      "iconoir",
      "icons8",
      "il",
      "ion",
      "iwwa",
      "jam",
      "la",
      "lets-icons",
      "line-md",
      "logos",
      "ls",
      "lucide",
      "lucide-lab",
      "mage",
      "majesticons",
      "maki",
      "map",
      "marketeq",
      "material-symbols",
      "material-symbols-light",
      "mdi",
      "mdi-light",
      "medical-icon",
      "memory",
      "meteocons",
      "mi",
      "mingcute",
      "mono-icons",
      "mynaui",
      "nimbus",
      "nonicons",
      "noto",
      "noto-v1",
      "octicon",
      "oi",
      "ooui",
      "openmoji",
      "oui",
      "pajamas",
      "pepicons",
      "pepicons-pencil",
      "pepicons-pop",
      "pepicons-print",
      "ph",
      "pixelarticons",
      "prime",
      "ps",
      "quill",
      "radix-icons",
      "raphael",
      "ri",
      "rivet-icons",
      "si-glyph",
      "simple-icons",
      "simple-line-icons",
      "skill-icons",
      "solar",
      "streamline",
      "streamline-emojis",
      "subway",
      "svg-spinners",
      "system-uicons",
      "tabler",
      "tdesign",
      "teenyicons",
      "token",
      "token-branded",
      "topcoat",
      "twemoji",
      "typcn",
      "uil",
      "uim",
      "uis",
      "uit",
      "uiw",
      "unjs",
      "vaadin",
      "vs",
      "vscode-icons",
      "websymbol",
      "weui",
      "whh",
      "wi",
      "wpf",
      "zmdi",
      "zondicons"
    ],
    "fetchTimeout": 1500
  }
};
const __appConfig = /* @__PURE__ */ defuFn(inlineConfig);
function useAppConfig() {
  const nuxtApp = useNuxtApp();
  nuxtApp._appConfig ||= klona(__appConfig);
  return nuxtApp._appConfig;
}
const plugin = /* @__PURE__ */ defineNuxtPlugin({
  name: "pinia",
  setup(nuxtApp) {
    const pinia = createPinia();
    nuxtApp.vueApp.use(pinia);
    setActivePinia(pinia);
    {
      nuxtApp.payload.pinia = pinia.state.value;
    }
    return {
      provide: {
        pinia
      }
    };
  }
});
const LazyIcon = defineAsyncComponent(() => Promise.resolve().then(() => index).then((r) => r["default"] || r.default || r));
const lazyGlobalComponents = [
  ["Icon", LazyIcon]
];
const components_plugin_z4hgvsiddfKkfXTP6M8M4zG5Cb7sGnDhcryKVM45Di4 = /* @__PURE__ */ defineNuxtPlugin({
  name: "nuxt:global-components",
  setup(nuxtApp) {
    for (const [name, component] of lazyGlobalComponents) {
      nuxtApp.vueApp.component(name, component);
      nuxtApp.vueApp.component("Lazy" + name, component);
    }
  }
});
const plugin_MeUvTuoKUi51yb_kBguab6hdcExVXeTtZtTg9TZZBB8 = /* @__PURE__ */ defineNuxtPlugin({
  name: "@nuxt/icon",
  setup() {
    const configs = /* @__PURE__ */ useRuntimeConfig();
    const options = useAppConfig().icon;
    _api.setFetch($fetch.native);
    const resources = [];
    if (options.provider === "server") {
      const baseURL2 = configs.app?.baseURL?.replace(/\/$/, "") ?? "";
      resources.push(baseURL2 + (options.localApiEndpoint || "/api/_nuxt_icon"));
      if (options.fallbackToApi === true || options.fallbackToApi === "client-only") {
        resources.push(options.iconifyApiEndpoint);
      }
    } else if (options.provider === "none") {
      _api.setFetch(() => Promise.resolve(new Response()));
    } else {
      resources.push(options.iconifyApiEndpoint);
    }
    async function customIconLoader(icons, prefix) {
      try {
        const data = await $fetch(resources[0] + "/" + prefix + ".json", {
          query: {
            icons: icons.join(",")
          }
        });
        if (!data || data.prefix !== prefix || !data.icons)
          throw new Error("Invalid data" + JSON.stringify(data));
        return data;
      } catch (e) {
        console.error("Failed to load custom icons", e);
        return null;
      }
    }
    addAPIProvider("", { resources });
    for (const prefix of options.customCollections || []) {
      if (prefix)
        setCustomIconsLoader(customIconLoader, prefix);
    }
  }
  // For type portability
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
});
const plugins = [
  unhead_k2P3m_ZDyjlr2mMYnoDPwavjsDN8hBlk9cFai0bbopU,
  router_DclsWNDeVV7SyG4lslgLnjbQUK1ws8wgf2FHaAbo7Cw,
  revive_payload_server_MVtmlZaQpj6ApFmshWfUWl5PehCebzaBf2NuRMiIbms,
  plugin,
  components_plugin_z4hgvsiddfKkfXTP6M8M4zG5Cb7sGnDhcryKVM45Di4,
  plugin_MeUvTuoKUi51yb_kBguab6hdcExVXeTtZtTg9TZZBB8
];
async function loadIcon(name, timeout) {
  if (!name)
    return null;
  const _icon = getIcon(name);
  if (_icon)
    return _icon;
  let timeoutWarn;
  const load = loadIcon$1(name).catch(() => {
    console.warn(`[Icon] failed to load icon \`${name}\``);
    return null;
  });
  if (timeout > 0)
    await Promise.race([
      load,
      new Promise((resolve) => {
        timeoutWarn = setTimeout(() => {
          console.warn(`[Icon] loading icon \`${name}\` timed out after ${timeout}ms`);
          resolve();
        }, timeout);
      })
    ]).finally(() => clearTimeout(timeoutWarn));
  else
    await load;
  return getIcon(name);
}
function useResolvedName(getName) {
  const options = useAppConfig().icon;
  const collections = (options.collections || []).sort((a, b) => b.length - a.length);
  return computed(() => {
    const name = getName();
    const bare = name.startsWith(options.cssSelectorPrefix) ? name.slice(options.cssSelectorPrefix.length) : name;
    const resolved = options.aliases?.[bare] || bare;
    if (!resolved.includes(":")) {
      const collection = collections.find((c) => resolved.startsWith(c + "-"));
      return collection ? collection + ":" + resolved.slice(collection.length + 1) : resolved;
    }
    return resolved;
  });
}
function resolveCustomizeFn(customize, globalCustomize) {
  if (customize === false) return void 0;
  if (customize === true || customize === null) return globalCustomize;
  return customize;
}
const SYMBOL_SERVER_CSS = "NUXT_ICONS_SERVER_CSS";
function escapeCssSelector(selector) {
  return selector.replace(/([^\w-])/g, "\\$1");
}
const NuxtIconCss = /* @__PURE__ */ defineComponent({
  name: "NuxtIconCss",
  props: {
    name: {
      type: String,
      required: true
    },
    customize: {
      type: [Function, Boolean, null],
      default: null,
      required: false
    }
  },
  setup(props) {
    const nuxt = useNuxtApp();
    const options = useAppConfig().icon;
    const cssClass = computed(() => props.name ? options.cssSelectorPrefix + props.name : "");
    const selector = computed(() => "." + escapeCssSelector(cssClass.value));
    function getCSS(icon, withLayer = true) {
      let iconSelector = selector.value;
      if (options.cssWherePseudo) {
        iconSelector = `:where(${iconSelector})`;
      }
      const css = getIconCSS(icon, {
        iconSelector,
        format: "compressed",
        customise: resolveCustomizeFn(props.customize, options.customize)
      });
      if (options.cssLayer && withLayer) {
        return `@layer ${options.cssLayer} { ${css} }`;
      }
      return css;
    }
    onServerPrefetch(async () => {
      {
        const configs = (/* @__PURE__ */ useRuntimeConfig()).icon || {};
        if (!configs?.serverKnownCssClasses?.includes(cssClass.value)) {
          const icon = await loadIcon(props.name, options.fetchTimeout).catch(() => null);
          if (!icon)
            return null;
          let ssrCSS = nuxt.vueApp._context.provides[SYMBOL_SERVER_CSS];
          if (!ssrCSS) {
            ssrCSS = nuxt.vueApp._context.provides[SYMBOL_SERVER_CSS] = /* @__PURE__ */ new Map();
            nuxt.runWithContext(() => {
              useHead({
                style: [
                  () => {
                    const sep = "";
                    let css = Array.from(ssrCSS.values()).sort().join(sep);
                    if (options.cssLayer) {
                      css = `@layer ${options.cssLayer} {${sep}${css}${sep}}`;
                    }
                    return { innerHTML: css };
                  }
                ]
              }, {
                tagPriority: "low"
              });
            });
          }
          if (props.name && !ssrCSS.has(props.name)) {
            const css = getCSS(icon, false);
            ssrCSS.set(props.name, css);
          }
          return null;
        }
      }
    });
    return () => h("span", { class: ["iconify", cssClass.value] });
  }
});
const NuxtIconSvg = /* @__PURE__ */ defineComponent({
  name: "NuxtIconSvg",
  props: {
    name: {
      type: String,
      required: true
    },
    customize: {
      type: [Function, Boolean, null],
      default: null,
      required: false
    }
  },
  setup(props, { slots }) {
    useNuxtApp();
    const options = useAppConfig().icon;
    const name = useResolvedName(() => props.name);
    const storeKey = "i-" + name.value;
    if (name.value) {
      onServerPrefetch(async () => {
        {
          await useAsyncData(
            storeKey,
            async () => await loadIcon(name.value, options.fetchTimeout),
            { deep: false }
          );
        }
      });
    }
    return () => h(Icon, {
      icon: name.value,
      ssr: true,
      // Iconify uses `customise`, where we expose `customize` for consistency
      customise: resolveCustomizeFn(props.customize, options.customize)
    }, slots);
  }
});
const __nuxt_component_0 = defineComponent({
  name: "NuxtIcon",
  props: {
    name: {
      type: String,
      required: true
    },
    mode: {
      type: String,
      required: false,
      default: null
    },
    size: {
      type: [Number, String],
      required: false,
      default: null
    },
    customize: {
      type: [Function, Boolean, null],
      default: null,
      required: false
    }
  },
  setup(props, { slots }) {
    const nuxtApp = useNuxtApp();
    const runtimeOptions = useAppConfig().icon;
    const name = useResolvedName(() => props.name);
    const component = computed(
      () => nuxtApp.vueApp?.component(name.value) || ((props.mode || runtimeOptions.mode) === "svg" ? NuxtIconSvg : NuxtIconCss)
    );
    const style = computed(() => {
      const size = props.size || runtimeOptions.size;
      return size ? { fontSize: Number.isNaN(+size) ? size : size + "px" } : null;
    });
    return () => h(
      component.value,
      {
        ...runtimeOptions.attrs,
        name: name.value,
        class: runtimeOptions.class,
        style: style.value,
        customize: props.customize
      },
      slots
    );
  }
});
const index = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  default: __nuxt_component_0
}, Symbol.toStringTag, { value: "Module" }));
var UserRole = /* @__PURE__ */ ((UserRole2) => {
  UserRole2["CLIENT"] = "client";
  UserRole2["EXPERT"] = "expert";
  UserRole2["ADMIN"] = "admin";
  return UserRole2;
})(UserRole || {});
var QuestionStatus = /* @__PURE__ */ ((QuestionStatus2) => {
  QuestionStatus2["PENDING"] = "pending";
  QuestionStatus2["PROCESSING"] = "processing";
  QuestionStatus2["AI_RESPONDED"] = "ai_responded";
  QuestionStatus2["EXPERT_REVIEW"] = "expert_review";
  QuestionStatus2["APPROVED"] = "approved";
  QuestionStatus2["REJECTED"] = "rejected";
  QuestionStatus2["COMPLETED"] = "completed";
  QuestionStatus2["FAILED"] = "failed";
  return QuestionStatus2;
})(QuestionStatus || {});
const useApi = () => {
  const config = /* @__PURE__ */ useRuntimeConfig();
  const baseURL2 = config.public.apiBase || "http://localhost:8000";
  const api = $fetch.create({
    baseURL: baseURL2,
    headers: {
      "Content-Type": "application/json"
    }
  });
  const login = async (email, password) => {
    return await api("/auth/login", {
      method: "POST",
      body: { email, password }
    });
  };
  const register = async (userData) => {
    return await api("/auth/register", {
      method: "POST",
      body: userData
    });
  };
  const registerClient = async (userData) => {
    return await api("/auth/register/client", {
      method: "POST",
      body: { ...userData, role: "client" }
    });
  };
  const registerExpert = async (userData) => {
    return await api("/auth/register/expert", {
      method: "POST",
      body: { ...userData, role: "expert" }
    });
  };
  const loginClient = async (email, password) => {
    return await api("/auth/login/client", {
      method: "POST",
      body: { email, password }
    });
  };
  const loginExpert = async (email, password) => {
    return await api("/auth/login/expert", {
      method: "POST",
      body: { email, password }
    });
  };
  const loginAdmin = async (email, password) => {
    return await api("/auth/login/admin", {
      method: "POST",
      body: { email, password }
    });
  };
  const submitQuestion = async (questionData) => {
    return await api("/questions/submit", {
      method: "POST",
      body: questionData
    });
  };
  const getQuestions = async (userId, status) => {
    const params = new URLSearchParams();
    if (userId) params.append("user_id", userId);
    if (status) params.append("status", status);
    return await api(`/questions?${params.toString()}`);
  };
  const getQuestionById = async (questionId) => {
    return await api(`/questions/${questionId}`);
  };
  const processWithAI = async (questionId) => {
    return await api(`/ai/process/${questionId}`, {
      method: "POST"
    });
  };
  const getAIResponse = async (questionId) => {
    return await api(`/ai/response/${questionId}`);
  };
  const getPendingReviews = async (expertId, subjects) => {
    return await api("/expert/reviews/pending", {
      method: "POST",
      body: { expertId, subjects }
    });
  };
  const submitExpertReview = async (reviewData) => {
    return await api("/expert/reviews/submit", {
      method: "POST",
      body: reviewData
    });
  };
  const queryPoeModels = async (models, question, subject) => {
    return await api("/poe/query-multiple", {
      method: "POST",
      body: { models, question, subject }
    });
  };
  const getPoeModels = async () => {
    return await api("/poe/models");
  };
  const humanizeResponse = async (responseId) => {
    return await api(`/humanization/process/${responseId}`, {
      method: "POST"
    });
  };
  const checkOriginality = async (responseId) => {
    return await api(`/originality/check/${responseId}`, {
      method: "POST"
    });
  };
  const getUsers = async () => {
    return await api("/admin/users");
  };
  const updateUserSubjects = async (userId, subjects) => {
    return await api(`/admin/users/${userId}/subjects`, {
      method: "PUT",
      body: { subjects }
    });
  };
  const getSystemStats = async () => {
    return await api("/admin/stats");
  };
  const connectWebSocket = (onMessage, onError) => {
    const wsUrl = config.public.wsUrl || "ws://localhost:8000/ws";
    const ws = new WebSocket(wsUrl);
    ws.onopen = () => {
      console.log("WebSocket connected");
    };
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error("WebSocket message parse error:", error);
      }
    };
    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      if (onError) onError(error);
    };
    ws.onclose = () => {
      console.log("WebSocket disconnected");
      setTimeout(() => {
        if (ws.readyState === WebSocket.CLOSED) {
          connectWebSocket(onMessage, onError);
        }
      }, 5e3);
    };
    return ws;
  };
  return {
    // Authentication
    login,
    register,
    registerClient,
    registerExpert,
    loginClient,
    loginExpert,
    loginAdmin,
    // Questions
    submitQuestion,
    getQuestions,
    getQuestionById,
    // AI Service
    processWithAI,
    getAIResponse,
    // Expert Reviews
    getPendingReviews,
    submitExpertReview,
    // Poe API
    queryPoeModels,
    getPoeModels,
    // Humanization & Originality
    humanizeResponse,
    checkOriginality,
    // Admin
    getUsers,
    updateUserSubjects,
    getSystemStats,
    // WebSocket
    connectWebSocket
  };
};
const useAuthStore = /* @__PURE__ */ defineStore("auth", {
  state: () => ({
    user: null,
    token: null,
    isLoading: false
  }),
  getters: {
    isAuthenticated: (state) => !!state.user && !!state.token,
    userRole: (state) => state.user?.role || null,
    userName: (state) => state.user?.name || "",
    userEmail: (state) => state.user?.email || "",
    userAvatar: (state) => state.user?.avatar || "",
    userInitials: (state) => {
      const name = state.user?.name || "";
      return name.split(" ").map((word) => word.charAt(0)).join("").toUpperCase().slice(0, 2);
    }
  },
  actions: {
    async login(email, password) {
      this.isLoading = true;
      try {
        const api = useApi();
        const response = await api.login(email, password);
        if (response.success) {
          this.user = response.user;
          this.token = response.access_token;
          if (false) ;
        } else {
          throw new Error(response.message || "Login failed");
        }
      } catch (error) {
        console.error("Login error:", error);
        throw new Error("Login failed. Please check your credentials.");
      } finally {
        this.isLoading = false;
      }
    },
    async register(email, password, name, role) {
      this.isLoading = true;
      try {
        const api = useApi();
        const nameParts = name.trim().split(" ");
        const firstName = nameParts[0] || "";
        const lastName = nameParts.slice(1).join(" ") || "";
        const payload = { email, password, first_name: firstName, last_name: lastName };
        const response = role === "client" ? await api.registerClient(payload) : role === "expert" ? await api.registerExpert(payload) : await api.register({ ...payload, role });
        if (response.success) {
          this.user = response.user;
          this.token = response.access_token;
          if (false) ;
        } else {
          throw new Error(response.message || "Registration failed");
        }
      } catch (error) {
        console.error("Registration error:", error);
        throw new Error("Registration failed. Please try again.");
      } finally {
        this.isLoading = false;
      }
    },
    async logout() {
      this.user = null;
      this.token = null;
    },
    async initializeAuth() {
    },
    hasRole(role) {
      return this.user?.role === role;
    }
  }
});
const useQuestionsStore = /* @__PURE__ */ defineStore("questions", {
  state: () => ({
    questions: [],
    isLoading: false,
    error: null
  }),
  getters: {
    getQuestionsByStatus: (state) => (status) => {
      return state.questions.filter((q) => q.status === status);
    },
    getQuestionsByUser: (state) => (userId) => {
      return state.questions.filter((q) => q.userId === userId);
    },
    pendingQuestions: (state) => state.questions.filter((q) => q.status === QuestionStatus.PENDING),
    completedQuestions: (state) => state.questions.filter((q) => q.status === QuestionStatus.COMPLETED)
  },
  actions: {
    async fetchQuestions(userId, status) {
      this.isLoading = true;
      this.error = null;
      try {
        const api = useApi();
        const response = await api.getQuestions(userId, status);
        if (response.success) {
          this.questions = response.data;
        } else {
          throw new Error(response.message || "Failed to fetch questions");
        }
      } catch (error) {
        console.error("Error fetching questions:", error);
        this.error = "Failed to fetch questions";
      } finally {
        this.isLoading = false;
      }
    },
    async submitQuestion(content, subject, userId, type = "text", imageUrl) {
      this.isLoading = true;
      this.error = null;
      try {
        const api = useApi();
        const response = await api.submitQuestion({
          content,
          subject,
          userId,
          type,
          imageUrl
        });
        if (response.success) {
          this.questions.unshift(response.data);
          return response;
        } else {
          throw new Error(response.message || "Failed to submit question");
        }
      } catch (error) {
        console.error("Submit question error:", error);
        this.error = "Failed to submit question";
        return {
          success: false,
          message: "Failed to submit question",
          error: error instanceof Error ? error.message : "Unknown error"
        };
      } finally {
        this.isLoading = false;
      }
    },
    async updateQuestionStatus(questionId, status) {
      this.isLoading = true;
      this.error = null;
      try {
        await new Promise((resolve) => setTimeout(resolve, 500));
        const question = this.questions.find((q) => q.id === questionId);
        if (question) {
          question.status = status;
          question.updatedAt = (/* @__PURE__ */ new Date()).toISOString();
        }
        return {
          success: true,
          message: "Question status updated successfully"
        };
      } catch (error) {
        this.error = "Failed to update question status";
        return {
          success: false,
          message: "Failed to update question status",
          error: "Failed to update question status"
        };
      } finally {
        this.isLoading = false;
      }
    },
    clearError() {
      this.error = null;
    }
  }
});
const _sfc_main$4 = /* @__PURE__ */ defineComponent({
  __name: "ExpertReviewPanel",
  __ssrInlineRender: true,
  setup(__props) {
    const authStore = useAuthStore();
    const pendingReviews = ref([]);
    const selectedReview = ref(null);
    const expertNotes = ref("");
    const isProcessing = ref(false);
    const isRefreshing = ref(false);
    const reviewedToday = ref(0);
    const approvalRate = ref(85);
    const expertSubjects = computed(() => {
      return authStore.user?.subjects || [];
    });
    const formatTime = (timestamp) => {
      const date = new Date(timestamp);
      const now = /* @__PURE__ */ new Date();
      const diff = now.getTime() - date.getTime();
      if (diff < 6e4) return "Just now";
      if (diff < 36e5) return `${Math.floor(diff / 6e4)}m ago`;
      if (diff < 864e5) return `${Math.floor(diff / 36e5)}h ago`;
      return date.toLocaleDateString();
    };
    return (_ctx, _push, _parent, _attrs) => {
      const _component_Icon = __nuxt_component_0;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "h-full bg-white flex flex-col" }, _attrs))}><div class="p-6 border-b border-gray-200"><div class="flex items-center justify-between mb-4"><div><h2 class="text-xl font-bold text-gray-900">Expert Review Panel</h2><p class="text-sm text-gray-500">Review and approve AI responses</p></div><div class="flex items-center space-x-2"><div class="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div><span class="text-xs text-gray-500">Online</span></div></div><div class="flex items-center space-x-2"><span class="text-sm font-medium text-gray-700">Your Subjects:</span><div class="flex flex-wrap gap-1"><!--[-->`);
      ssrRenderList(unref(expertSubjects), (subject) => {
        _push(`<span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">${ssrInterpolate(subject)}</span>`);
      });
      _push(`<!--]--></div></div></div><div class="px-6 py-4 bg-gray-50 border-b border-gray-200"><div class="grid grid-cols-3 gap-4"><div class="text-center"><div class="text-2xl font-bold text-yellow-600">${ssrInterpolate(unref(pendingReviews).length)}</div><div class="text-xs text-gray-500">Pending</div></div><div class="text-center"><div class="text-2xl font-bold text-green-600">${ssrInterpolate(unref(reviewedToday))}</div><div class="text-xs text-gray-500">Reviewed Today</div></div><div class="text-center"><div class="text-2xl font-bold text-blue-600">${ssrInterpolate(unref(approvalRate))}%</div><div class="text-xs text-gray-500">Approval Rate</div></div></div></div><div class="flex-1 overflow-y-auto"><div class="p-6"><div class="flex items-center justify-between mb-4"><h3 class="text-lg font-semibold text-gray-900">Review Queue</h3><button class="p-2 rounded-lg hover:bg-gray-100 transition-colors"${ssrIncludeBooleanAttr(unref(isRefreshing)) ? " disabled" : ""}>`);
      _push(ssrRenderComponent(_component_Icon, {
        name: "heroicons:arrow-path",
        class: ["h-4 w-4", { "animate-spin": unref(isRefreshing) }]
      }, null, _parent));
      _push(`</button></div>`);
      if (unref(pendingReviews).length === 0) {
        _push(`<div class="text-center py-12">`);
        _push(ssrRenderComponent(_component_Icon, {
          name: "heroicons:check-circle",
          class: "h-16 w-16 text-gray-300 mx-auto mb-4"
        }, null, _parent));
        _push(`<h4 class="text-lg font-medium text-gray-900 mb-2">All caught up!</h4><p class="text-gray-500">No pending reviews for your subjects.</p></div>`);
      } else {
        _push(`<div class="space-y-4"><!--[-->`);
        ssrRenderList(unref(pendingReviews), (review) => {
          _push(`<div class="${ssrRenderClass([{ "border-blue-300 bg-blue-50": unref(selectedReview)?.id === review.id }, "p-4 border border-gray-200 rounded-lg cursor-pointer hover:border-blue-300 hover:shadow-sm transition-all"])}"><div class="flex items-start justify-between mb-3"><div class="flex-1"><div class="flex items-center space-x-2 mb-2"><span class="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full">${ssrInterpolate(review.subject)}</span><span class="text-xs text-gray-500">${ssrInterpolate(formatTime(review.submittedAt))}</span></div><h4 class="text-sm font-medium text-gray-900 mb-2 line-clamp-2">${ssrInterpolate(review.question)}</h4><p class="text-xs text-gray-500"> Asked by: ${ssrInterpolate(review.userName)}</p></div><div class="flex items-center space-x-2"><div class="w-2 h-2 bg-yellow-400 rounded-full"></div>`);
          _push(ssrRenderComponent(_component_Icon, {
            name: "heroicons:chevron-right",
            class: "h-4 w-4 text-gray-400"
          }, null, _parent));
          _push(`</div></div></div>`);
        });
        _push(`<!--]--></div>`);
      }
      _push(`</div></div>`);
      if (unref(selectedReview)) {
        _push(`<div class="border-t border-gray-200 bg-gray-50"><div class="p-6"><div class="flex items-center justify-between mb-4"><h3 class="text-lg font-semibold text-gray-900">Review Details</h3><button class="p-1 rounded hover:bg-gray-200">`);
        _push(ssrRenderComponent(_component_Icon, {
          name: "heroicons:x-mark",
          class: "h-4 w-4"
        }, null, _parent));
        _push(`</button></div><div class="space-y-4"><div><label class="block text-sm font-medium text-gray-700 mb-2">Original Question</label><div class="p-3 bg-white border border-gray-200 rounded-lg"><p class="text-sm text-gray-900">${ssrInterpolate(unref(selectedReview).question)}</p><div class="flex items-center justify-between mt-2"><span class="text-xs text-gray-500">Subject: ${ssrInterpolate(unref(selectedReview).subject)}</span><span class="text-xs text-gray-500">${ssrInterpolate(formatTime(unref(selectedReview).submittedAt))}</span></div></div></div><div><label class="block text-sm font-medium text-gray-700 mb-2">AI Response</label><div class="p-3 bg-white border border-gray-200 rounded-lg"><p class="text-sm text-gray-900 whitespace-pre-wrap">${ssrInterpolate(unref(selectedReview).aiResponse)}</p></div></div><div><label class="block text-sm font-medium text-gray-700 mb-2">Expert Notes (Optional)</label><textarea class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none" rows="3" placeholder="Add any notes about your review decision...">${ssrInterpolate(unref(expertNotes))}</textarea></div><div class="flex space-x-3 pt-4"><button${ssrIncludeBooleanAttr(unref(isProcessing)) ? " disabled" : ""} class="flex-1 flex items-center justify-center space-x-2 bg-green-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">`);
        _push(ssrRenderComponent(_component_Icon, {
          name: "heroicons:check",
          class: "h-4 w-4"
        }, null, _parent));
        _push(`<span>Approve</span></button><button${ssrIncludeBooleanAttr(unref(isProcessing)) ? " disabled" : ""} class="flex-1 flex items-center justify-center space-x-2 bg-red-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">`);
        _push(ssrRenderComponent(_component_Icon, {
          name: "heroicons:x-mark",
          class: "h-4 w-4"
        }, null, _parent));
        _push(`<span>Reject</span></button></div></div></div></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div>`);
    };
  }
});
const _sfc_setup$4 = _sfc_main$4.setup;
_sfc_main$4.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/ExpertReviewPanel.vue");
  return _sfc_setup$4 ? _sfc_setup$4(props, ctx) : void 0;
};
const _sfc_main$3 = /* @__PURE__ */ defineComponent({
  __name: "AdminPanel",
  __ssrInlineRender: true,
  setup(__props) {
    const expertUsers = ref([]);
    ref(false);
    return (_ctx, _push, _parent, _attrs) => {
      const _component_Icon = __nuxt_component_0;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "h-full bg-white border-l border-gray-200 shadow-lg" }, _attrs))}><div class="p-6"><h2 class="text-lg font-semibold text-gray-900 mb-4">Admin Dashboard</h2><div class="grid grid-cols-2 gap-4 mb-6"><div class="bg-blue-50 p-4 rounded-lg"><div class="flex items-center">`);
      _push(ssrRenderComponent(_component_Icon, {
        name: "heroicons:question-mark-circle",
        class: "h-8 w-8 text-blue-600"
      }, null, _parent));
      _push(`<div class="ml-3"><p class="text-sm font-medium text-blue-600">Total Questions</p><p class="text-2xl font-bold text-blue-900">1,247</p></div></div></div><div class="bg-green-50 p-4 rounded-lg"><div class="flex items-center">`);
      _push(ssrRenderComponent(_component_Icon, {
        name: "heroicons:users",
        class: "h-8 w-8 text-green-600"
      }, null, _parent));
      _push(`<div class="ml-3"><p class="text-sm font-medium text-green-600">Active Users</p><p class="text-2xl font-bold text-green-900">342</p></div></div></div><div class="bg-yellow-50 p-4 rounded-lg"><div class="flex items-center">`);
      _push(ssrRenderComponent(_component_Icon, {
        name: "heroicons:clock",
        class: "h-8 w-8 text-yellow-600"
      }, null, _parent));
      _push(`<div class="ml-3"><p class="text-sm font-medium text-yellow-600">Pending Reviews</p><p class="text-2xl font-bold text-yellow-900">23</p></div></div></div><div class="bg-purple-50 p-4 rounded-lg"><div class="flex items-center">`);
      _push(ssrRenderComponent(_component_Icon, {
        name: "heroicons:chart-bar",
        class: "h-8 w-8 text-purple-600"
      }, null, _parent));
      _push(`<div class="ml-3"><p class="text-sm font-medium text-purple-600">Success Rate</p><p class="text-2xl font-bold text-purple-900">94.2%</p></div></div></div></div><div class="space-y-4"><h3 class="text-sm font-medium text-gray-700">Recent Activity</h3><div class="space-y-3"><div class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">`);
      _push(ssrRenderComponent(_component_Icon, {
        name: "heroicons:plus-circle",
        class: "h-5 w-5 text-green-600"
      }, null, _parent));
      _push(`<div class="flex-1"><p class="text-sm text-gray-900">New question submitted</p><p class="text-xs text-gray-500">Mathematics - 2 minutes ago</p></div></div><div class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">`);
      _push(ssrRenderComponent(_component_Icon, {
        name: "heroicons:check-circle",
        class: "h-5 w-5 text-blue-600"
      }, null, _parent));
      _push(`<div class="flex-1"><p class="text-sm text-gray-900">Question approved by expert</p><p class="text-xs text-gray-500">Physics - 5 minutes ago</p></div></div><div class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">`);
      _push(ssrRenderComponent(_component_Icon, {
        name: "heroicons:user-plus",
        class: "h-5 w-5 text-purple-600"
      }, null, _parent));
      _push(`<div class="flex-1"><p class="text-sm text-gray-900">New user registered</p><p class="text-xs text-gray-500">Student - 10 minutes ago</p></div></div></div></div><div class="mt-6 pt-6 border-t border-gray-200"><h3 class="text-sm font-medium text-gray-700 mb-3">Expert Management</h3><div class="space-y-3"><!--[-->`);
      ssrRenderList(unref(expertUsers), (expert) => {
        _push(`<div class="p-3 bg-white border border-gray-200 rounded-lg"><div class="flex items-center justify-between mb-2"><div class="flex items-center space-x-2"><div class="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center"><span class="text-xs font-medium text-blue-600">${ssrInterpolate(expert.name.charAt(0))}</span></div><span class="text-sm font-medium text-gray-900">${ssrInterpolate(expert.name)}</span></div><span class="text-xs text-gray-500">${ssrInterpolate(expert.subjects?.length || 0)} subjects</span></div><div class="flex flex-wrap gap-1"><!--[-->`);
        ssrRenderList(expert.subjects || [], (subject) => {
          _push(`<span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">${ssrInterpolate(subject)}</span>`);
        });
        _push(`<!--]-->`);
        if (!expert.subjects || expert.subjects.length === 0) {
          _push(`<button class="text-xs text-gray-500 hover:text-blue-600"> Assign subjects </button>`);
        } else {
          _push(`<!---->`);
        }
        _push(`</div></div>`);
      });
      _push(`<!--]--></div></div><div class="mt-6 pt-6 border-t border-gray-200"><h3 class="text-sm font-medium text-gray-700 mb-3">Quick Actions</h3><div class="space-y-2"><button class="w-full btn-secondary text-sm">`);
      _push(ssrRenderComponent(_component_Icon, {
        name: "heroicons:cog-6-tooth",
        class: "h-4 w-4"
      }, null, _parent));
      _push(` System Settings </button><button class="w-full btn-secondary text-sm">`);
      _push(ssrRenderComponent(_component_Icon, {
        name: "heroicons:users",
        class: "h-4 w-4"
      }, null, _parent));
      _push(` Manage Users </button><button class="w-full btn-secondary text-sm">`);
      _push(ssrRenderComponent(_component_Icon, {
        name: "heroicons:chart-bar-square",
        class: "h-4 w-4"
      }, null, _parent));
      _push(` View Analytics </button></div></div></div></div>`);
    };
  }
});
const _sfc_setup$3 = _sfc_main$3.setup;
_sfc_main$3.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/AdminPanel.vue");
  return _sfc_setup$3 ? _sfc_setup$3(props, ctx) : void 0;
};
const _sfc_main$2 = /* @__PURE__ */ defineComponent({
  __name: "app",
  __ssrInlineRender: true,
  setup(__props) {
    const authStore = useAuthStore();
    useQuestionsStore();
    const isLoading = ref(true);
    const showSidebar = ref(true);
    const showExpertPanel = ref(false);
    const showLoginModal = ref(false);
    const showAttachmentOptions = ref(false);
    const isSignupMode = ref(false);
    const loginForm = ref({
      email: "",
      password: ""
    });
    const signupForm = ref({
      firstName: "",
      lastName: "",
      email: "",
      password: "",
      role: ""
    });
    const chatHistory = ref([]);
    const selectedChat = ref(null);
    const currentMessage = ref("");
    const newChatSubject = ref("");
    const isTyping = ref(false);
    ref();
    ref();
    ref();
    const canSendMessage = computed(() => {
      if (!authStore.isAuthenticated) return false;
      if (!currentMessage.value.trim()) return false;
      if (!selectedChat.value && authStore.hasRole("client") && !newChatSubject.value) return false;
      return true;
    });
    const getRoleDisplayName = (role) => {
      switch (role) {
        case UserRole.CLIENT:
          return "Student";
        case UserRole.EXPERT:
          return "Expert Editor";
        case UserRole.ADMIN:
          return "System Admin";
        default:
          return "User";
      }
    };
    const getChatIcon = (chat) => {
      switch (chat.subject) {
        case "Mathematics":
          return "heroicons:calculator";
        case "Physics":
          return "heroicons:bolt";
        case "Chemistry":
          return "heroicons:beaker";
        case "Biology":
          return "heroicons:heart";
        case "Computer Science":
          return "heroicons:computer-desktop";
        case "Engineering":
          return "heroicons:cog-6-tooth";
        case "Business":
          return "heroicons:briefcase";
        default:
          return "heroicons:question-mark-circle";
      }
    };
    const getMessageClasses = (message) => {
      if (message.sender === "user") {
        return "bg-gradient-to-r from-blue-500 to-purple-600 text-white";
      } else if (message.sender === "ai") {
        return "bg-white border border-gray-200 text-gray-900 shadow-sm";
      } else if (message.sender === "expert") {
        return "bg-blue-50 border border-blue-200 text-blue-900";
      } else {
        return "bg-gray-100 border border-gray-200 text-gray-700";
      }
    };
    const getMessageIcon = (message) => {
      switch (message.sender) {
        case "user":
          return "heroicons:user";
        case "ai":
          return "heroicons:cpu-chip";
        case "expert":
          return "heroicons:academic-cap";
        case "system":
          return "heroicons:information-circle";
        default:
          return "heroicons:chat-bubble-left-right";
      }
    };
    const getMessageSender = (message) => {
      switch (message.sender) {
        case "user":
          return "You";
        case "ai":
          return "AI Assistant";
        case "expert":
          return "Expert Review";
        case "system":
          return "System";
        default:
          return "Unknown";
      }
    };
    const getStatusBadgeClass = (status) => {
      switch (status.toLowerCase()) {
        case "pending":
          return "bg-yellow-100 text-yellow-800";
        case "processing":
          return "bg-blue-100 text-blue-800";
        case "ai_responded":
          return "bg-purple-100 text-purple-800";
        case "expert_review":
          return "bg-orange-100 text-orange-800";
        case "approved":
          return "bg-green-100 text-green-800";
        case "rejected":
          return "bg-red-100 text-red-800";
        case "completed":
          return "bg-green-100 text-green-800";
        case "failed":
          return "bg-red-100 text-red-800";
        default:
          return "bg-gray-100 text-gray-800";
      }
    };
    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    };
    const formatChatTime = (timestamp) => {
      const date = new Date(timestamp);
      const now = /* @__PURE__ */ new Date();
      const diff = now.getTime() - date.getTime();
      if (diff < 6e4) return "Just now";
      if (diff < 36e5) return `${Math.floor(diff / 6e4)}m ago`;
      if (diff < 864e5) return `${Math.floor(diff / 36e5)}h ago`;
      return date.toLocaleDateString();
    };
    useHead({
      title: "AL-Tech Academy Q&A System",
      meta: [
        { name: "description", content: "AI-Powered Q&A System for AL-Tech Academy" },
        { name: "viewport", content: "width=device-width, initial-scale=1" }
      ]
    });
    useSeoMeta({
      title: "AL-Tech Academy Q&A System",
      ogTitle: "AL-Tech Academy Q&A System",
      description: "AI-Powered Q&A System for AL-Tech Academy",
      ogDescription: "AI-Powered Q&A System for AL-Tech Academy",
      ogImage: "/og-image.jpg",
      twitterCard: "summary_large_image"
    });
    return (_ctx, _push, _parent, _attrs) => {
      const _component_Icon = __nuxt_component_0;
      _push(`<div${ssrRenderAttrs(mergeProps({
        id: "app",
        class: "h-screen bg-gray-100 flex"
      }, _attrs))}>`);
      if (unref(isLoading)) {
        _push(`<div class="fixed inset-0 bg-white/90 backdrop-blur-sm z-50 flex items-center justify-center"><div class="flex flex-col items-center space-y-4"><div class="spinner w-8 h-8"></div><p class="text-gray-600 font-medium">Loading AL-Tech Academy Q&amp;A...</p></div></div>`);
      } else {
        _push(`<div class="flex w-full h-full"><div class="${ssrRenderClass([{ "hidden lg:flex": !unref(showSidebar) }, "w-80 bg-white border-r border-gray-200 flex flex-col"])}"><div class="p-4 border-b border-gray-200"><div class="flex items-center justify-between"><div class="flex items-center space-x-3"><div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">`);
        _push(ssrRenderComponent(_component_Icon, {
          name: "heroicons:academic-cap",
          class: "h-6 w-6 text-white"
        }, null, _parent));
        _push(`</div><div><h1 class="text-lg font-semibold text-gray-900">AL-Tech Academy</h1><p class="text-xs text-gray-500">AI-Powered Q&amp;A</p></div></div><button class="lg:hidden p-2 rounded-lg hover:bg-gray-100">`);
        _push(ssrRenderComponent(_component_Icon, {
          name: "heroicons:x-mark",
          class: "h-5 w-5"
        }, null, _parent));
        _push(`</button></div></div>`);
        if (unref(authStore).isAuthenticated) {
          _push(`<div class="p-4 border-b border-gray-200"><div class="flex items-center space-x-3"><div class="w-10 h-10 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center"><span class="text-sm font-bold text-white">${ssrInterpolate(unref(authStore).userInitials)}</span></div><div class="flex-1 min-w-0"><p class="text-sm font-medium text-gray-900 truncate">${ssrInterpolate(unref(authStore).userName)}</p><p class="text-xs text-gray-500">${ssrInterpolate(getRoleDisplayName(unref(authStore).userRole))}</p></div><button class="p-1 rounded hover:bg-gray-100">`);
          _push(ssrRenderComponent(_component_Icon, {
            name: "heroicons:arrow-right-on-rectangle",
            class: "h-4 w-4 text-gray-400"
          }, null, _parent));
          _push(`</button></div></div>`);
        } else {
          _push(`<div class="p-4 border-b border-gray-200"><button class="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-2 px-4 rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200"> Sign In to Start </button></div>`);
        }
        _push(`<div class="flex-1 overflow-y-auto"><div class="p-4"><h3 class="text-sm font-medium text-gray-700 mb-3">Recent Conversations</h3><div class="space-y-2"><!--[-->`);
        ssrRenderList(unref(chatHistory), (chat) => {
          _push(`<div class="${ssrRenderClass([{ "bg-blue-50 border border-blue-200": unref(selectedChat)?.id === chat.id }, "p-3 rounded-lg cursor-pointer transition-colors hover:bg-gray-50"])}"><div class="flex items-start space-x-3"><div class="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">`);
          _push(ssrRenderComponent(_component_Icon, {
            name: getChatIcon(chat),
            class: "h-4 w-4 text-gray-600"
          }, null, _parent));
          _push(`</div><div class="flex-1 min-w-0"><p class="text-sm font-medium text-gray-900 truncate">${ssrInterpolate(chat.title)}</p><p class="text-xs text-gray-500 truncate">${ssrInterpolate(chat.lastMessage)}</p><p class="text-xs text-gray-400">${ssrInterpolate(formatChatTime(chat.updatedAt))}</p></div>`);
          if (chat.status === "pending") {
            _push(`<div class="w-2 h-2 bg-yellow-400 rounded-full"></div>`);
          } else if (chat.status === "processing") {
            _push(`<div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>`);
          } else if (chat.status === "completed") {
            _push(`<div class="w-2 h-2 bg-green-400 rounded-full"></div>`);
          } else {
            _push(`<!---->`);
          }
          _push(`</div></div>`);
        });
        _push(`<!--]-->`);
        if (unref(chatHistory).length === 0) {
          _push(`<div class="text-center py-8">`);
          _push(ssrRenderComponent(_component_Icon, {
            name: "heroicons:chat-bubble-left-ellipsis",
            class: "h-12 w-12 text-gray-300 mx-auto mb-2"
          }, null, _parent));
          _push(`<p class="text-sm text-gray-500">No conversations yet</p><p class="text-xs text-gray-400">Start asking questions!</p></div>`);
        } else {
          _push(`<!---->`);
        }
        _push(`</div></div></div><div class="p-4 border-t border-gray-200"><button class="w-full flex items-center justify-center space-x-2 bg-white border border-gray-300 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-50 transition-colors">`);
        _push(ssrRenderComponent(_component_Icon, {
          name: "heroicons:plus",
          class: "h-4 w-4"
        }, null, _parent));
        _push(`<span>New Question</span></button></div></div><div class="flex-1 flex flex-col"><div class="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between"><div class="flex items-center space-x-4"><button class="lg:hidden p-2 rounded-lg hover:bg-gray-100">`);
        _push(ssrRenderComponent(_component_Icon, {
          name: "heroicons:bars-3",
          class: "h-5 w-5"
        }, null, _parent));
        _push(`</button>`);
        if (unref(selectedChat)) {
          _push(`<div><h2 class="text-lg font-semibold text-gray-900">${ssrInterpolate(unref(selectedChat).title)}</h2><p class="text-sm text-gray-500">${ssrInterpolate(unref(selectedChat).subject)}</p></div>`);
        } else {
          _push(`<div><h2 class="text-lg font-semibold text-gray-900">AL-Tech Academy Q&amp;A</h2><p class="text-sm text-gray-500">Ask me anything!</p></div>`);
        }
        _push(`</div><div class="flex items-center space-x-2">`);
        if (unref(selectedChat)?.status) {
          _push(`<div class="flex items-center space-x-2"><span class="${ssrRenderClass([getStatusBadgeClass(unref(selectedChat).status), "text-xs px-2 py-1 rounded-full"])}">${ssrInterpolate(unref(selectedChat).status)}</span></div>`);
        } else {
          _push(`<!---->`);
        }
        if (unref(authStore).hasRole("expert") || unref(authStore).hasRole("admin")) {
          _push(`<button class="p-2 rounded-lg hover:bg-gray-100">`);
          _push(ssrRenderComponent(_component_Icon, {
            name: "heroicons:cog-6-tooth",
            class: "h-5 w-5 text-gray-600"
          }, null, _parent));
          _push(`</button>`);
        } else {
          _push(`<!---->`);
        }
        _push(`</div></div><div class="flex-1 overflow-y-auto bg-gray-50"><div class="max-w-4xl mx-auto p-6 space-y-6">`);
        if (!unref(selectedChat) || !unref(selectedChat).messages || unref(selectedChat).messages.length === 0) {
          _push(`<div class="text-center py-12"><div class="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">`);
          _push(ssrRenderComponent(_component_Icon, {
            name: "heroicons:academic-cap",
            class: "h-10 w-10 text-white"
          }, null, _parent));
          _push(`</div><h3 class="text-2xl font-bold text-gray-900 mb-3">Welcome to AL-Tech Academy</h3><p class="text-gray-600 max-w-md mx-auto mb-8"> Get instant, accurate answers to your academic questions powered by advanced AI technology. </p><button class="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200"> Start Your First Question </button></div>`);
        } else {
          _push(`<!---->`);
        }
        if (unref(selectedChat)) {
          _push(`<div class="space-y-4"><!--[-->`);
          ssrRenderList(unref(selectedChat).messages, (message) => {
            _push(`<div class="${ssrRenderClass([message.sender === "user" ? "justify-end" : "justify-start", "flex"])}"><div class="${ssrRenderClass([getMessageClasses(message), "max-w-2xl px-4 py-3 rounded-2xl"])}">`);
            if (message.sender !== "user") {
              _push(`<div class="flex items-center space-x-2 mb-2">`);
              _push(ssrRenderComponent(_component_Icon, {
                name: getMessageIcon(message),
                class: "h-4 w-4"
              }, null, _parent));
              _push(`<span class="text-xs font-medium text-gray-600">${ssrInterpolate(getMessageSender(message))}</span></div>`);
            } else {
              _push(`<!---->`);
            }
            _push(`<div class="prose prose-sm max-w-none">`);
            if (message.type === "text") {
              _push(`<div>${message.content ?? ""}</div>`);
            } else if (message.type === "image") {
              _push(`<div class="space-y-2"><img${ssrRenderAttr("src", message.imageUrl)}${ssrRenderAttr("alt", message.content)} class="max-w-sm rounded-lg shadow-sm"><p class="text-sm text-gray-600">${ssrInterpolate(message.content)}</p></div>`);
            } else {
              _push(`<!---->`);
            }
            _push(`</div><div class="flex items-center justify-between mt-2"><span class="text-xs text-gray-400">${ssrInterpolate(formatTime(message.timestamp))}</span>`);
            if (message.status) {
              _push(`<div class="flex items-center space-x-2"><span class="${ssrRenderClass([getStatusBadgeClass(message.status), "text-xs px-2 py-1 rounded-full"])}">${ssrInterpolate(message.status)}</span></div>`);
            } else {
              _push(`<!---->`);
            }
            _push(`</div></div></div>`);
          });
          _push(`<!--]-->`);
          if (unref(isTyping)) {
            _push(`<div class="flex justify-start"><div class="bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm"><div class="flex items-center space-x-2"><div class="flex space-x-1"><div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div><div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="${ssrRenderStyle({ "animation-delay": "0.1s" })}"></div><div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="${ssrRenderStyle({ "animation-delay": "0.2s" })}"></div></div><span class="text-sm text-gray-500">AI is thinking...</span></div></div></div>`);
          } else {
            _push(`<!---->`);
          }
          _push(`</div>`);
        } else {
          _push(`<!---->`);
        }
        _push(`</div></div><div class="bg-white border-t border-gray-200 p-4"><div class="max-w-4xl mx-auto"><form class="flex items-end space-x-3">`);
        if (!unref(selectedChat) && unref(authStore).hasRole("client")) {
          _push(`<div class="w-48"><select class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"><option value=""${ssrIncludeBooleanAttr(Array.isArray(unref(newChatSubject)) ? ssrLooseContain(unref(newChatSubject), "") : ssrLooseEqual(unref(newChatSubject), "")) ? " selected" : ""}>Select Subject</option><option value="Mathematics"${ssrIncludeBooleanAttr(Array.isArray(unref(newChatSubject)) ? ssrLooseContain(unref(newChatSubject), "Mathematics") : ssrLooseEqual(unref(newChatSubject), "Mathematics")) ? " selected" : ""}>Mathematics</option><option value="Physics"${ssrIncludeBooleanAttr(Array.isArray(unref(newChatSubject)) ? ssrLooseContain(unref(newChatSubject), "Physics") : ssrLooseEqual(unref(newChatSubject), "Physics")) ? " selected" : ""}>Physics</option><option value="Chemistry"${ssrIncludeBooleanAttr(Array.isArray(unref(newChatSubject)) ? ssrLooseContain(unref(newChatSubject), "Chemistry") : ssrLooseEqual(unref(newChatSubject), "Chemistry")) ? " selected" : ""}>Chemistry</option><option value="Biology"${ssrIncludeBooleanAttr(Array.isArray(unref(newChatSubject)) ? ssrLooseContain(unref(newChatSubject), "Biology") : ssrLooseEqual(unref(newChatSubject), "Biology")) ? " selected" : ""}>Biology</option><option value="Computer Science"${ssrIncludeBooleanAttr(Array.isArray(unref(newChatSubject)) ? ssrLooseContain(unref(newChatSubject), "Computer Science") : ssrLooseEqual(unref(newChatSubject), "Computer Science")) ? " selected" : ""}>Computer Science</option><option value="Engineering"${ssrIncludeBooleanAttr(Array.isArray(unref(newChatSubject)) ? ssrLooseContain(unref(newChatSubject), "Engineering") : ssrLooseEqual(unref(newChatSubject), "Engineering")) ? " selected" : ""}>Engineering</option><option value="Business"${ssrIncludeBooleanAttr(Array.isArray(unref(newChatSubject)) ? ssrLooseContain(unref(newChatSubject), "Business") : ssrLooseEqual(unref(newChatSubject), "Business")) ? " selected" : ""}>Business</option><option value="Other"${ssrIncludeBooleanAttr(Array.isArray(unref(newChatSubject)) ? ssrLooseContain(unref(newChatSubject), "Other") : ssrLooseEqual(unref(newChatSubject), "Other")) ? " selected" : ""}>Other</option></select></div>`);
        } else {
          _push(`<!---->`);
        }
        _push(`<div class="flex-1 relative"><textarea placeholder="Type your question..." class="w-full px-4 py-3 border border-gray-300 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" rows="1">${ssrInterpolate(unref(currentMessage))}</textarea><button type="button" class="absolute right-3 bottom-3 p-1 rounded-full hover:bg-gray-100">`);
        _push(ssrRenderComponent(_component_Icon, {
          name: "heroicons:paper-clip",
          class: "h-5 w-5 text-gray-500"
        }, null, _parent));
        _push(`</button></div><button type="submit"${ssrIncludeBooleanAttr(!unref(canSendMessage)) ? " disabled" : ""} class="p-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-full hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200">`);
        _push(ssrRenderComponent(_component_Icon, {
          name: "heroicons:paper-airplane",
          class: "h-5 w-5"
        }, null, _parent));
        _push(`</button></form>`);
        if (unref(showAttachmentOptions)) {
          _push(`<div class="mt-3 p-3 bg-gray-50 rounded-lg"><div class="flex space-x-3"><button class="flex items-center space-x-2 px-3 py-2 bg-white rounded-lg border border-gray-200 hover:border-blue-300 transition-colors">`);
          _push(ssrRenderComponent(_component_Icon, {
            name: "heroicons:photo",
            class: "h-4 w-4 text-gray-600"
          }, null, _parent));
          _push(`<span class="text-sm">Upload Image</span></button><button class="flex items-center space-x-2 px-3 py-2 bg-white rounded-lg border border-gray-200 hover:border-blue-300 transition-colors">`);
          _push(ssrRenderComponent(_component_Icon, {
            name: "heroicons:document",
            class: "h-4 w-4 text-gray-600"
          }, null, _parent));
          _push(`<span class="text-sm">Upload File</span></button></div></div>`);
        } else {
          _push(`<!---->`);
        }
        _push(`</div></div></div>`);
        if (unref(showExpertPanel) && (unref(authStore).hasRole("expert") || unref(authStore).hasRole("admin"))) {
          _push(`<div class="w-96 bg-white border-l border-gray-200">`);
          if (unref(authStore).hasRole("expert")) {
            _push(ssrRenderComponent(_sfc_main$4, null, null, _parent));
          } else if (unref(authStore).hasRole("admin")) {
            _push(ssrRenderComponent(_sfc_main$3, null, null, _parent));
          } else {
            _push(`<!---->`);
          }
          _push(`</div>`);
        } else {
          _push(`<!---->`);
        }
        _push(`</div>`);
      }
      if (unref(showLoginModal)) {
        _push(`<div class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center"><div class="bg-white rounded-2xl p-8 w-full max-w-md mx-4"><div class="text-center mb-6"><div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">`);
        _push(ssrRenderComponent(_component_Icon, {
          name: "heroicons:academic-cap",
          class: "h-8 w-8 text-white"
        }, null, _parent));
        _push(`</div><h2 class="text-2xl font-bold text-gray-900 mb-2">${ssrInterpolate(unref(isSignupMode) ? "Create Account" : "Welcome Back")}</h2><p class="text-gray-600">${ssrInterpolate(unref(isSignupMode) ? "Join AL-Tech Academy today" : "Sign in to your account")}</p></div><div class="flex mb-6 bg-gray-100 rounded-lg p-1"><button class="${ssrRenderClass([
          "flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors",
          !unref(isSignupMode) ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-700"
        ])}"> Sign In </button><button class="${ssrRenderClass([
          "flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors",
          unref(isSignupMode) ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-700"
        ])}"> Sign Up </button></div>`);
        if (!unref(isSignupMode)) {
          _push(`<form class="space-y-4"><div><label for="login-email" class="block text-sm font-medium text-gray-700 mb-1"> Email Address </label><input id="login-email"${ssrRenderAttr("value", unref(loginForm).email)} type="email" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" placeholder="Enter your email"></div><div><label for="login-password" class="block text-sm font-medium text-gray-700 mb-1"> Password </label><input id="login-password"${ssrRenderAttr("value", unref(loginForm).password)} type="password" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" placeholder="Enter your password"></div><button type="submit"${ssrIncludeBooleanAttr(unref(authStore).isLoading) ? " disabled" : ""} class="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-4 rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200">`);
          if (unref(authStore).isLoading) {
            _push(`<span class="flex items-center justify-center"><div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div> Signing In... </span>`);
          } else {
            _push(`<span>Sign In</span>`);
          }
          _push(`</button></form>`);
        } else {
          _push(`<form class="space-y-4"><div class="grid grid-cols-2 gap-4"><div><label for="signup-firstname" class="block text-sm font-medium text-gray-700 mb-1"> First Name </label><input id="signup-firstname"${ssrRenderAttr("value", unref(signupForm).firstName)} type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" placeholder="First name"></div><div><label for="signup-lastname" class="block text-sm font-medium text-gray-700 mb-1"> Last Name </label><input id="signup-lastname"${ssrRenderAttr("value", unref(signupForm).lastName)} type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" placeholder="Last name"></div></div><div><label for="signup-email" class="block text-sm font-medium text-gray-700 mb-1"> Email Address </label><input id="signup-email"${ssrRenderAttr("value", unref(signupForm).email)} type="email" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" placeholder="Enter your email"></div><div><label for="signup-password" class="block text-sm font-medium text-gray-700 mb-1"> Password </label><input id="signup-password"${ssrRenderAttr("value", unref(signupForm).password)} type="password" required minlength="8" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" placeholder="Create a password (min 8 characters)"></div><div><label for="signup-role" class="block text-sm font-medium text-gray-700 mb-1"> Role </label><select id="signup-role" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"><option value=""${ssrIncludeBooleanAttr(Array.isArray(unref(signupForm).role) ? ssrLooseContain(unref(signupForm).role, "") : ssrLooseEqual(unref(signupForm).role, "")) ? " selected" : ""}>Select your role</option><option value="client"${ssrIncludeBooleanAttr(Array.isArray(unref(signupForm).role) ? ssrLooseContain(unref(signupForm).role, "client") : ssrLooseEqual(unref(signupForm).role, "client")) ? " selected" : ""}>Student - Ask Questions</option><option value="expert"${ssrIncludeBooleanAttr(Array.isArray(unref(signupForm).role) ? ssrLooseContain(unref(signupForm).role, "expert") : ssrLooseEqual(unref(signupForm).role, "expert")) ? " selected" : ""}>Expert - Review Answers</option><option value="admin"${ssrIncludeBooleanAttr(Array.isArray(unref(signupForm).role) ? ssrLooseContain(unref(signupForm).role, "admin") : ssrLooseEqual(unref(signupForm).role, "admin")) ? " selected" : ""}>Admin - System Management</option></select></div><button type="submit"${ssrIncludeBooleanAttr(unref(authStore).isLoading) ? " disabled" : ""} class="w-full bg-gradient-to-r from-green-500 to-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:from-green-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200">`);
          if (unref(authStore).isLoading) {
            _push(`<span class="flex items-center justify-center"><div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div> Creating Account... </span>`);
          } else {
            _push(`<span>Create Account</span>`);
          }
          _push(`</button></form>`);
        }
        _push(`<div class="mt-6 pt-6 border-t border-gray-200"><p class="text-center text-sm text-gray-500 mb-3">Or try with demo accounts</p><div class="grid grid-cols-3 gap-2"><button class="px-3 py-2 text-xs bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"> Student </button><button class="px-3 py-2 text-xs bg-orange-50 text-orange-700 rounded-lg hover:bg-orange-100 transition-colors"> Expert </button><button class="px-3 py-2 text-xs bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition-colors"> Admin </button></div></div><button class="mt-6 w-full text-sm text-gray-500 hover:text-gray-700 transition-colors"> Maybe Later </button></div></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<input type="file" accept="image/*" class="hidden"></div>`);
    };
  }
});
const _sfc_setup$2 = _sfc_main$2.setup;
_sfc_main$2.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("app.vue");
  return _sfc_setup$2 ? _sfc_setup$2(props, ctx) : void 0;
};
const _sfc_main$1 = {
  __name: "nuxt-error-page",
  __ssrInlineRender: true,
  props: {
    error: Object
  },
  setup(__props) {
    const props = __props;
    const _error = props.error;
    _error.stack ? _error.stack.split("\n").splice(1).map((line) => {
      const text = line.replace("webpack:/", "").replace(".vue", ".js").trim();
      return {
        text,
        internal: line.includes("node_modules") && !line.includes(".cache") || line.includes("internal") || line.includes("new Promise")
      };
    }).map((i) => `<span class="stack${i.internal ? " internal" : ""}">${i.text}</span>`).join("\n") : "";
    const statusCode = Number(_error.statusCode || 500);
    const is404 = statusCode === 404;
    const statusMessage = _error.statusMessage ?? (is404 ? "Page Not Found" : "Internal Server Error");
    const description = _error.message || _error.toString();
    const stack = void 0;
    const _Error404 = defineAsyncComponent(() => import('./error-404-BgbUGAFU.mjs'));
    const _Error = defineAsyncComponent(() => import('./error-500-CI1gwLUa.mjs'));
    const ErrorTemplate = is404 ? _Error404 : _Error;
    return (_ctx, _push, _parent, _attrs) => {
      _push(ssrRenderComponent(unref(ErrorTemplate), mergeProps({ statusCode: unref(statusCode), statusMessage: unref(statusMessage), description: unref(description), stack: unref(stack) }, _attrs), null, _parent));
    };
  }
};
const _sfc_setup$1 = _sfc_main$1.setup;
_sfc_main$1.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("node_modules/nuxt/dist/app/components/nuxt-error-page.vue");
  return _sfc_setup$1 ? _sfc_setup$1(props, ctx) : void 0;
};
const _sfc_main = {
  __name: "nuxt-root",
  __ssrInlineRender: true,
  setup(__props) {
    const IslandRenderer = () => null;
    const nuxtApp = useNuxtApp();
    nuxtApp.deferHydration();
    nuxtApp.ssrContext.url;
    const SingleRenderer = false;
    provide(PageRouteSymbol, useRoute());
    nuxtApp.hooks.callHookWith((hooks) => hooks.map((hook) => hook()), "vue:setup");
    const error = /* @__PURE__ */ useError();
    const abortRender = error.value && !nuxtApp.ssrContext.error;
    onErrorCaptured((err, target, info) => {
      nuxtApp.hooks.callHook("vue:error", err, target, info).catch((hookError) => console.error("[nuxt] Error in `vue:error` hook", hookError));
      {
        const p = nuxtApp.runWithContext(() => showError(err));
        onServerPrefetch(() => p);
        return false;
      }
    });
    const islandContext = nuxtApp.ssrContext.islandContext;
    return (_ctx, _push, _parent, _attrs) => {
      ssrRenderSuspense(_push, {
        default: () => {
          if (unref(abortRender)) {
            _push(`<div></div>`);
          } else if (unref(error)) {
            _push(ssrRenderComponent(unref(_sfc_main$1), { error: unref(error) }, null, _parent));
          } else if (unref(islandContext)) {
            _push(ssrRenderComponent(unref(IslandRenderer), { context: unref(islandContext) }, null, _parent));
          } else if (unref(SingleRenderer)) {
            ssrRenderVNode(_push, createVNode(resolveDynamicComponent(unref(SingleRenderer)), null, null), _parent);
          } else {
            _push(ssrRenderComponent(unref(_sfc_main$2), null, null, _parent));
          }
        },
        _: 1
      });
    };
  }
};
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("node_modules/nuxt/dist/app/components/nuxt-root.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
let entry;
{
  entry = async function createNuxtAppServer(ssrContext) {
    const vueApp = createApp(_sfc_main);
    const nuxt = createNuxtApp({ vueApp, ssrContext });
    try {
      await applyPlugins(nuxt, plugins);
      await nuxt.hooks.callHook("app:created", vueApp);
    } catch (error) {
      await nuxt.hooks.callHook("app:error", error);
      nuxt.payload.error ||= createError(error);
    }
    if (ssrContext?._renderResponse) {
      throw new Error("skipping render");
    }
    return vueApp;
  };
}
const entry$1 = (ssrContext) => entry(ssrContext);

export { useNuxtApp as a, useRuntimeConfig as b, nuxtLinkDefaults as c, useHead as d, entry$1 as default, navigateTo as n, resolveRouteObject as r, useRouter as u };
//# sourceMappingURL=server.mjs.map
