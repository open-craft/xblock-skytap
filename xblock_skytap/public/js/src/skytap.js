/* Javascript for the Skytap XBlock. */

function SkytapXBlock(runtime, element) {
    "use strict";

    var launchForm = $('.skytap-launch-form', element),
        launchButton = launchForm.find('.skytap-launch'),
        launchXHR;

    launchButton.on('click', function(e) {
        e.preventDefault();

        var handlerUrl = runtime.handlerUrl(element, 'launch'),
            keyboardLayout = launchForm.find('select').val();

        if (launchXHR) {
            launchXHR.abort();
        }

        launchButton[0].setAttribute('disabled', 'true');

        launchXHR = $.post(handlerUrl, JSON.stringify(keyboardLayout))
            .success(function(response) {
                var url = response.sharing_portal_url;
                var sharingPortal = window.open(url, '_blank');
                if (sharingPortal === null) {
                    alert("The browser's popup blocker prevented the exercise environment from being launched.");
                } else {
                    sharingPortal.focus();
                }

                launchButton[0].removeAttribute('disabled');
            })
            .error(function(jqXHR, textStatus, errorThrown) {
                var error;
                if (jqXHR.hasOwnProperty('responseJSON') && jqXHR.responseJSON.hasOwnProperty('error')) {
                    error = jqXHR.responseJSON.error;
                } else {
                    error = 'An unknown error occurred while launching.';
                }
                $('#skytap-error').text('Error: ' + error);

                launchButton[0].removeAttribute('disabled');
            });

    });

}
