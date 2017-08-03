'use strict'

urlBase = ''
authHeader = 'Authorization'

getHost = (url)->
    m = url.match(/^(?:https?:)?\/\/([^\/]+)/)
    if m then return m[1]
    null

urlBaseHost = getHost(urlBase) || location.host




angular.module("{{SERVICE_PREFIX_NAME}}Services", ['ngResource'])

.config([ "$resourceProvider", "$httpProvider", ($resourceProvider, $httpProvider)->
    $resourceProvider.defaults.stripTrailingSlashes = false
    $httpProvider.defaults.xsrfCookieName = 'csrftoken'
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
])


{% for modelName,conf in API.items %}

.factory("{{modelName}}", [ "CustomResource", "{{SERVICE_PREFIX_NAME}}Auth", (Resource, {{SERVICE_PREFIX_NAME}}Auth)->
    R = Resource(
        urlBase + "{{conf.commonUrl}}",
        { {% for param in conf.commonUrlParams %}
            {{param}}: '@{{param}}',{% endfor %}
        },
        { {% for actionName,actionConf in conf.api.items %}
            "{{actionName}}":{
                url: urlBase + "{{actionConf.url}}",
                method: "{{actionConf.method}}",{% for on,ov in actionConf.options.items %}
                {{on}}: {{ov}}{% endfor %}{% if actionName == 'login' or actionName == 'register' %}
                interceptor: {
                    response: (response)->
                        data = response.data
                        {{SERVICE_PREFIX_NAME}}Auth.setUser(data.token, data.userId, data.user)
                        params = response.config.params or {}
                        {{SERVICE_PREFIX_NAME}}Auth.rememberMe = !!params.rememberMe
                        {{SERVICE_PREFIX_NAME}}Auth.save()
                        response.resource
                }{% endif %}{% if actionName == 'logout' %}
                interceptor: {
                    response: (response)->
                        {{SERVICE_PREFIX_NAME}}Auth.clearUser()
                        {{SERVICE_PREFIX_NAME}}Auth.clearStorage()
                        response.resource
                }{% endif %}
            }{% endfor %}
        }
    )
    {% for alias,toAction in conf.alias.items %}
    R['{{alias}}'] = R['{{toAction}}']{% endfor %}
    R.modelName = "{{modelName}}"
    R
])

{% endfor %}







.factory('{{SERVICE_PREFIX_NAME}}Auth', ->
    props = [
        'accessTokenId'
        'currentUserId'
        'rememberMe'
    ]
    propsPrefix = '${{SERVICE_PREFIX_NAME}}$'

    {{SERVICE_PREFIX_NAME}}Auth = ->
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

    {{SERVICE_PREFIX_NAME}}Auth::save = ->
        self = this
        storage = if @rememberMe then localStorage else sessionStorage
        if !localStorage and !storage
            console.warn('{{SERVICE_PREFIX_NAME}}Auth: localStorage is unavailable, using sessionStorage')
            storage = sessionStorage
        props.forEach (name) ->
            save storage, name, self[name]
            return
        return

    {{SERVICE_PREFIX_NAME}}Auth::setUser = (accessTokenId, userId, userData) ->
        @accessTokenId = accessTokenId
        @currentUserId = userId
        @currentUserData = userData
        return

    {{SERVICE_PREFIX_NAME}}Auth::clearUser = ->
        @accessTokenId = null
        @currentUserId = null
        @currentUserData = null
        return

    {{SERVICE_PREFIX_NAME}}Auth::clearStorage = ->
        props.forEach (name) ->
            save(sessionStorage, name, null)
            if localStorage then save(localStorage, name, null)
            return
        return

    new {{SERVICE_PREFIX_NAME}}Auth
)

.config([
    '$httpProvider'
    ($httpProvider) ->
        $httpProvider.interceptors.push '{{SERVICE_PREFIX_NAME}}AuthRequestInterceptor'
        return
])

.factory('{{SERVICE_PREFIX_NAME}}AuthRequestInterceptor', [
    '$q'
    '{{SERVICE_PREFIX_NAME}}Auth'
    ($q, {{SERVICE_PREFIX_NAME}}Auth) ->
        request: (config) ->
            # filter out external requests
            host = getHost(config.url)
            if host and host != urlBaseHost
                return config
            if {{SERVICE_PREFIX_NAME}}Auth.accessTokenId
                config.headers[authHeader] = "Token " + {{SERVICE_PREFIX_NAME}}Auth.accessTokenId
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





.provider('CustomResource', ()->
    ###*
    # @ngdoc method
    # @name {{SERVICE_PREFIX_NAME}}Services.CustomResourceProvider#setAuthHeader
    # @methodOf {{SERVICE_PREFIX_NAME}}Services.CustomResourceProvider
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
    # @name {{SERVICE_PREFIX_NAME}}Services.CustomResourceProvider#setUrlBase
    # @methodOf {{SERVICE_PREFIX_NAME}}Services.CustomResourceProvider
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
    # @name {{SERVICE_PREFIX_NAME}}Services.CustomResourceProvider#getUrlBase
    # @methodOf {{SERVICE_PREFIX_NAME}}Services.CustomResourceProvider
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
