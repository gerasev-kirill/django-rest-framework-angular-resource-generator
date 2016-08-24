'use strict'

urlBase = ''
authHeader = 'authorization'

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

.factory("{{modelName}}", [ "DjResource", (Resource)->
    R = Resource(
        urlBase + "{{conf.commonUrl}}",{% if conf.hasIdInUrl %}
        {id: '@id'},{% else %}
        {},{% endif %}
        { {% for actionName,actionConf in conf.api.items %}
            "{{actionName}}":{
                url: urlBase + "{{actionConf.url}}",
                method: "{{actionConf.method}}",{% for on,ov in actionConf.options.items %}
                {{on}}: {{ov}}{% endfor %}
            }{% endfor %}
        }
    )
    {% for alias,toAction in conf.alias.items %}
    R['{{alias}}'] = R['{{toAction}}']{% endfor %}
    R.$modelName = "{{modelName}}"
    R
])

{% endfor %}

.provider 'DjResource', ()->
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

                resource::$save = (success, error) ->
                    # Fortunately, LoopBack provides a convenient `upsert` method
                    # that exactly fits our needs.
                    result = resource.update.call(this, {}, this, success, error)
                    result.$promise or result

                resource
    ]
    return
