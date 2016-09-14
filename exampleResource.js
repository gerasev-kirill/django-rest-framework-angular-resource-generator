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

    angular.module("djServices", ['ngResource']).config(function($resourceProvider, $httpProvider) {
        $resourceProvider.defaults.stripTrailingSlashes = false;
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    })


    .factory("users", [
        "DjResource", "djAuth", function(Resource, djAuth) {
            var R;
            R = Resource(urlBase + "/users/:id/",
            {
                id: '@id'
            },
            {
                "retrieve": {
                    url: urlBase + "/users/:id/",
                    method: "GET",
                },
                "create": {
                    url: urlBase + "/users/",
                    method: "POST",
                },
                "list": {
                    url: urlBase + "/users/",
                    method: "GET",
                    isArray: true
                },
                "update": {
                    url: urlBase + "/users/:id/",
                    method: "PUT",
                },
                "partialUpdate": {
                    url: urlBase + "/users/:id/",
                    method: "PATCH",
                },
                "destroy": {
                    url: urlBase + "/users/:id/",
                    method: "DELETE",
                },
            });

            R['destroyById'] = R['destroy'];
            R['deleteById'] = R['destroy'];
            R['findById'] = R['retrieve'];
            R.$modelName = "users";
            return R;
        }
    ])

    .factory("Article", [
        "DjResource", "djAuth", function(Resource, djAuth) {
            var R;
            R = Resource(urlBase + "/articles/:id/",
            {
                id: '@id'
            },
            {
                "create": {
                    url: urlBase + "/articles/",
                    method: "GET",
                    isArray: true
                },
                "destroy": {
                    url: urlBase + "/articles/:id/",
                    method: "DELETE",
                },
                "update": {
                    url: urlBase + "/articles/:id/",
                    method: "PATCH",
                },
            });

            R['destroyById'] = R['destroy'];
            R['deleteById'] = R['destroy'];
            R.$modelName = "Article";
            return R;
        }
    ])


    .factory('djAuth', function() {
        var djAuth, load, props, propsPrefix, save;
        props = ['accessTokenId', 'currentUserId', 'rememberMe'];
        propsPrefix = '$dj$';
        djAuth = function() {
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
            return localStorage[key] || sessionStorage[key] || null;
        };
        djAuth.prototype.save = function() {
            var self, storage;
            self = this;
            storage = this.rememberMe ? localStorage : sessionStorage;
            props.forEach(function(name) {
                save(storage, name, self[name]);
            });
        };
        djAuth.prototype.setUser = function(accessTokenId, userId, userData) {
            this.accessTokenId = accessTokenId;
            this.currentUserId = userId;
            this.currentUserData = userData;
        };
        djAuth.prototype.clearUser = function() {
            this.accessTokenId = null;
            this.currentUserId = null;
            this.currentUserData = null;
        };
        djAuth.prototype.clearStorage = function() {
            props.forEach(function(name) {
                save(sessionStorage, name, null);
                save(localStorage, name, null);
            });
        };
        return new djAuth;
    })
    .config([
        '$httpProvider', function($httpProvider) {
            $httpProvider.interceptors.push('djAuthRequestInterceptor');
        }
    ])
    .factory('djAuthRequestInterceptor', [
        '$q', 'djAuth', function($q, djAuth) {
            return {
                request: function(config) {
                    var host, res;
                    host = getHost(config.url);
                    if (host && host !== urlBaseHost) {
                        return config;
                    }
                    if (djAuth.accessTokenId) {
                        config.headers[authHeader] = "Token " + djAuth.accessTokenId;
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
    .provider('DjResource', function() {

        /**
         * @ngdoc method
         * @name djServices.DjResourceProvider#setAuthHeader
         * @methodOf djServices.DjResourceProvider
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
         * @name djServices.DjResourceProvider#setUrlBase
         * @methodOf djServices.DjResourceProvider
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
         * @name djServices.DjResourceProvider#getUrlBase
         * @methodOf djServices.DjResourceProvider
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
                    resource.prototype.$save = function(success, error) {
                        var result;
                        result = resource.update.call(this, {}, this, success, error);
                        return result.$promise || result;
                    };
                    return resource;
                };
            }
        ];
    });

}).call(this);
