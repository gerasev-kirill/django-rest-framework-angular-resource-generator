'use strict'

urlBase = ''
authHeader = 'Authorization'

getHost = (url)->
    m = url.match(/^(?:https?:)?\/\/([^\/]+)/)
    if m then return m[1]
    null

urlBaseHost = getHost(urlBase) || location.host




angular.module("djServices", ['ngResource'])

.config ($resourceProvider, $httpProvider)->
    $resourceProvider.defaults.stripTrailingSlashes = false
    $httpProvider.defaults.xsrfCookieName = 'csrftoken'
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'



{% for modelName,conf in API.items %}

.factory("{{modelName}}", [ "DjResource", "djAuth", (Resource, djAuth)->
    R = Resource(
        urlBase + "{{conf.commonUrl}}",{% if conf.hasIdInUrl %}
        {id: '@id'},{% else %}
        {},{% endif %}
        { {% for actionName,actionConf in conf.api.items %}
            "{{actionName}}":{
                url: urlBase + "{{actionConf.url}}",
                method: "{{actionConf.method}}",{% for on,ov in actionConf.options.items %}
                {{on}}: {{ov}}{% endfor %}{% if actionName == 'login' or actionName == 'register' %}
                interceptor: {
                    response: (response)->
                        data = response.data
                        djAuth.setUser(data.token, data.userId, data.user)
                        params = response.config.params or {}
                        djAuth.rememberMe = !!params.rememberMe
                        djAuth.save()
                        response.resource
                }{% endif %}{% if actionName == 'logout' %}
                interceptor: {
                    response: (response)->
                        djAuth.clearUser()
                        djAuth.clearStorage()
                        response.resource
                }{% endif %}
            }{% endfor %}
        }
    )
    {% for alias,toAction in conf.alias.items %}
    R['{{alias}}'] = R['{{toAction}}']{% endfor %}
    R.$modelName = "{{modelName}}"
    R
])

{% endfor %}







.factory('djAuth', ->
    props = [
        'accessTokenId'
        'currentUserId'
        'rememberMe'
    ]
    propsPrefix = '$dj$'

    djAuth = ->
        self = this
        props.forEach (name) ->
            self[name] = load(name)
            return
        @currentUserData = null
        return

    # Note: LocalStorage converts the value to string
    # We are using empty string as a marker for null/undefined values.

    save = (storage, name, value) ->
        key = propsPrefix + name
        if value == null
            value = ''
        storage[key] = value
        return

    load = (name) ->
        key = propsPrefix + name
        if localStorage
            return localStorage[key] or sessionStorage[key] or null
        sessionStorage[key] or null

    djAuth::save = ->
        self = this
        storage = if @rememberMe then localStorage else sessionStorage
        if !localStorage and !storage
            console.warn('LoopBackAuth: localStorage is unavailable, using sessionStorage')
            storage = sessionStorage
        props.forEach (name) ->
            save storage, name, self[name]
            return
        return

    djAuth::setUser = (accessTokenId, userId, userData) ->
        @accessTokenId = accessTokenId
        @currentUserId = userId
        @currentUserData = userData
        return

    djAuth::clearUser = ->
        @accessTokenId = null
        @currentUserId = null
        @currentUserData = null
        return

    djAuth::clearStorage = ->
        props.forEach (name) ->
            save sessionStorage, name, null
            save localStorage, name, null
            return
        return

    new djAuth
)

.config([
    '$httpProvider'
    ($httpProvider) ->
        $httpProvider.interceptors.push 'djAuthRequestInterceptor'
        return
])

.factory('djAuthRequestInterceptor', [
    '$q'
    'djAuth'
    ($q, djAuth) ->
        request: (config) ->
            # filter out external requests
            host = getHost(config.url)
            if host and host != urlBaseHost
                return config
            if djAuth.accessTokenId
                config.headers[authHeader] = "Token " + djAuth.accessTokenId
            else if config.__isGetCurrentUser__
                # Return a stub 401 error for User.getCurrent() when
                # there is no user logged in
                res =
                    body: error: status: 401
                    status: 401
                    config: config
                    headers: ->
                        undefined
                return $q.reject(res)
            config or $q.when(config)
])





.provider('DjResource', ()->
    ###*
    # @ngdoc method
    # @name djServices.DjResourceProvider#setAuthHeader
    # @methodOf djServices.DjResourceProvider
    # @param {string} header The header name to use, e.g. `X-Access-Token`
    # @description
    # Configure the REST transport to use a different header for sending
    # the authentication token. It is sent in the `Authorization` header
    # by default.
    ###

    @setAuthHeader = (header) ->
        authHeader = header
        return

    ###*
    # @ngdoc method
    # @name djServices.DjResourceProvider#setUrlBase
    # @methodOf djServices.DjResourceProvider
    # @param {string} url The URL to use, e.g. `/api` or `//example.com/api`.
    # @description
    # Change the URL of the REST API server. By default, the URL provided
    # to the code generator (`lb-ng` or `grunt-loopback-sdk-angular`) is used.
    ###

    @setUrlBase = (url) ->
        urlBase = url
        urlBaseHost = getHost(urlBase) or location.host
        return

    ###*
    # @ngdoc method
    # @name djServices.DjResourceProvider#getUrlBase
    # @methodOf djServices.DjResourceProvider
    # @description
    # Get the URL of the REST API server. The URL provided
    # to the code generator (`lb-ng` or `grunt-loopback-sdk-angular`) is used.
    ###

    @getUrlBase = ->
        urlBase

    @$get = [
        '$resource'
        ($resource) ->
            (url, params, actions) ->
                resource = $resource(url, params, actions)
                # Angular always calls POST on $save()
                # This hack is based on
                # http://kirkbushell.me/angular-js-using-ng-resource-in-a-more-restful-manner/
                resource::$origSave = resource::$save

                resource::$save = (success, error) ->
                    # create new object
                    if not this.hasOwnProperty('id') and not this.hasOwnProperty('pk')
                        if resource.create
                            result = resource.create.call(this, {}, this, success, error)
                            return result.$promise or result
                        return resource.$origSave(success, error)
                    # update old object
                    result = resource.update.call(this, {}, this, success, error)
                    result.$promise or result

                resource
    ]
    return
)
