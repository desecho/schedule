var spinner_options = {
    lines: 12,
    length: 5,
    width: 3,
    radius: 6,
    corners: 1,
    rotate: 40,
    color: '#000',
    speed: 1,
    trail: 60,
    shadow: false,
    hwaccel: true,
    className: 'spinner',
    zIndex: 2e9,
    top: 'auto',
    left: 'auto'
};

angular.module('loadingIndicator', [])
    .config(function ($httpProvider) {
        $httpProvider.responseInterceptors.push('myHttpInterceptor');
        var spinnerFunction = function (data, headersGetter) {
            // todo start the spinner here
            $('#loading').spin(spinner_options);
            return data;
        };
        $httpProvider.defaults.transformRequest.push(spinnerFunction);
    })
// register the interceptor as a service, intercepts ALL angular ajax http calls
    .factory('myHttpInterceptor', function ($q, $window) {
        return function (promise) {
            return promise.then(function (response) {
                // do something on success
                // todo hide the spinner
                $('#loading').spin(false);
                return response;

            }, function (response) {
                // do something on error
                // todo hide the spinner
                $('#loading').spin(false);
                return $q.reject(response);
            });
        };
    });
