(function() {
    'use strict';
    var authHeader, getHost, urlBase, urlBaseHost;

    urlBase = '';

    authHeader = 'Authorization';

    getHost = function(url) {
        var m;
        m = url.match(/^(?:https?:)?\/\/([^\/]+)/);
        if (m) {
            return m[1];
        }
        return null;
    };

    urlBaseHost = getHost(urlBase) || location.host;

    angular.module("{{SERVICE_PREFIX_NAME}}Services", ['ngResource']).config(function($resourceProvider, $httpProvider) {
        $resourceProvider.defaults.stripTrailingSlashes = false;
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    })

    {% for modelName,conf in API.items %}
    .factory("{{modelName}}", [
        "CustomResource", "{{SERVICE_PREFIX_NAME}}Auth", function(Resource, {{SERVICE_PREFIX_NAME}}Auth) {
            var R;
            R = Resource(urlBase + "{{conf.commonUrl}}",
            { {% for param in conf.commonUrlParams %}
                {{param}}: '@{{param}}',{% endfor %}
            },
            { {% for actionName,actionConf in conf.api.items %}
                "{{actionName}}": {
                    url: urlBase + "{{actionConf.url}}",
                    method: "{{actionConf.method}}", {% for on,ov in actionConf.options.items %}
                    {{on}}: {{ov}}{% endfor %}{% if actionName == 'login' or actionName == 'register' %}
                    interceptor: {
                        response: function(response) {
                            var data, params;
                            data = response.data;
                            {{SERVICE_PREFIX_NAME}}Auth.setUser(data.token, data.userId, data.user);
                            params = response.config.params || {};
                            {{SERVICE_PREFIX_NAME}}Auth.rememberMe = !!params.rememberMe;
                            {{SERVICE_PREFIX_NAME}}Auth.save();
                            return response.resource;
                        }
                    },{% endif %}{% if actionName == 'logout' %}
                    interceptor: {
                        response: function(response) {
                            {{SERVICE_PREFIX_NAME}}Auth.clearUser();
                            {{SERVICE_PREFIX_NAME}}Auth.clearStorage();
                            return response.resource;
                        }
                    }{% endif %}
                },{% endfor %}
            });
            {% for alias,toAction in conf.alias.items %}
            R['{{alias}}'] = R['{{toAction}}'];{% endfor %}
            R.modelName = "{{modelName}}";
            return R;
        }
    ])
    {% endfor %}

    .factory('{{SERVICE_PREFIX_NAME}}Auth', function() {
        var {{SERVICE_PREFIX_NAME}}Auth, load, props, propsPrefix, save;
        props = ['accessTokenId', 'currentUserId', 'rememberMe'];
        propsPrefix = '${{SERVICE_PREFIX_NAME}}$';
        {{SERVICE_PREFIX_NAME}}Auth = function() {
            var self;
            self = this;
            props.forEach(function(name) {
                self[name] = load(name);
            });
            this.currentUserData = null;
        };
        save = function(storage, name, value) {
            var key;
            key = propsPrefix + name;
            if (value === null) {
                value = '';
            }
            storage[key] = value;
        };
        load = function(name) {
            var key;
            key = propsPrefix + name;
            if (localStorage){
               return localStorage[key] || sessionStorage[key] || null;
            }
            return sessionStorage[key] || null;
        };
        {{SERVICE_PREFIX_NAME}}Auth.prototype.save = function() {
            var self, storage;
            self = this;
            storage = this.rememberMe ? localStorage : sessionStorage;
            if (!localStorage && !storage){
                console.warn('{{SERVICE_PREFIX_NAME}}Auth: localStorage is unavailable, using sessionStorage');
                storage = sessionStorage;
            }
            props.forEach(function(name) {
                save(storage, name, self[name]);
            });
        };
        {{SERVICE_PREFIX_NAME}}Auth.prototype.setUser = function(accessTokenId, userId, userData) {
            this.accessTokenId = accessTokenId;
            this.currentUserId = userId;
            this.currentUserData = userData;
        };
        {{SERVICE_PREFIX_NAME}}Auth.prototype.clearUser = function() {
            this.accessTokenId = null;
            this.currentUserId = null;
            this.currentUserData = null;
        };
        {{SERVICE_PREFIX_NAME}}Auth.prototype.clearStorage = function() {
            props.forEach(function(name) {
                save(sessionStorage, name, null);
                if (localStorage){
                    save(localStorage, name, null);
                }
            });
        };
        return new {{SERVICE_PREFIX_NAME}}Auth;
    })
    .config([
        '$httpProvider', function($httpProvider) {
            $httpProvider.interceptors.push('{{SERVICE_PREFIX_NAME}}AuthRequestInterceptor');
        }
    ])
    .factory('{{SERVICE_PREFIX_NAME}}AuthRequestInterceptor', [
        '$q', '{{SERVICE_PREFIX_NAME}}Auth', function($q, {{SERVICE_PREFIX_NAME}}Auth) {
            return {
                request: function(config) {
                    var host, res;
                    host = getHost(config.url);
                    if (host && host !== urlBaseHost) {
                        return config;
                    }
                    if ({{SERVICE_PREFIX_NAME}}Auth.accessTokenId) {
                        config.headers[authHeader] = "Token " + {{SERVICE_PREFIX_NAME}}Auth.accessTokenId;
                    } else if (config.__isGetCurrentUser__) {
                        res = {
                            body: {
                                error: {
                                    status: 401
                                }
                            },
                            status: 401,
                            config: config,
                            headers: function() {
                                return void 0;
                            }
                        };
                        return $q.reject(res);
                    }
                    return config || $q.when(config);
                }
            };
        }
    ])
    .provider('CustomResource', function() {

        /**
         * @ngdoc method
         * @name {{SERVICE_PREFIX_NAME}}Services.CustomResourceProvider#setAuthHeader
         * @methodOf {{SERVICE_PREFIX_NAME}}Services.CustomResourceProvider
         * @param {string} header The header name to use, e.g. `X-Access-Token`
         * @description
         * Configure the REST transport to use a different header for sending
         * the authentication token. It is sent in the `Authorization` header
         * by default.
         */
        this.setAuthHeader = function(header) {
            authHeader = header;
        };

        /**
         * @ngdoc method
         * @name {{SERVICE_PREFIX_NAME}}Services.CustomResourceProvider#setUrlBase
         * @methodOf {{SERVICE_PREFIX_NAME}}Services.CustomResourceProvider
         * @param {string} url The URL to use, e.g. `/api` or `//example.com/api`.
         * @description
         * Change the URL of the REST API server. By default, the URL provided
         * to the code generator (`lb-ng` or `grunt-loopback-sdk-angular`) is used.
         */
        this.setUrlBase = function(url) {
            urlBase = url;
            urlBaseHost = getHost(urlBase) || location.host;
        };

        /**
         * @ngdoc method
         * @name {{SERVICE_PREFIX_NAME}}Services.CustomResourceProvider#getUrlBase
         * @methodOf {{SERVICE_PREFIX_NAME}}Services.CustomResourceProvider
         * @description
         * Get the URL of the REST API server. The URL provided
         * to the code generator (`lb-ng` or `grunt-loopback-sdk-angular`) is used.
         */
        this.getUrlBase = function() {
            return urlBase;
        };
        this.$get = [
            '$resource', function($resource) {
                return function(url, params, actions) {
                    var resource;
                    resource = $resource(url, params, actions);
                    // Angular always calls POST on $save()
                    // This hack is based on
                    // http://kirkbushell.me/angular-js-using-ng-resource-in-a-more-restful-manner/

                    resource.prototype.$origSave = resource.prototype.$save;

                    resource.prototype.$save = function(success, error) {
                        var result;
                        // create new object
                        if (!this.hasOwnProperty('id') && !this.hasOwnProperty('pk')) {
                            if (resource.create) {
                                result = resource.create.call(this, {}, this, success, error);
                                return result.$promise || result;
                            }
                            return resource.$origSave(success, error);
                        }
                        //  update old object
                        result = resource.update.call(this, {}, this, success, error);
                        return result.$promise || result;
                    };
                    return resource;
                };
            }
        ];
    });

}).call(this);
