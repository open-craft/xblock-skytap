/* Javascript for the Skytap XBlock. */

function SkytapXBlock(runtime, element) {
    "use strict";

    // Set up gettext in case it isn't available in the client runtime:
    if (typeof gettext == 'undefined') {
        window.gettext = function gettext_stub(string) { return string; };
        window.ngettext = function ngettext_stub(strA, strB, n) { return n == 1 ? strA : strB; };
    }

    var launchForm = $('.skytap-launch-form', element),
        launchButton = launchForm.find('.skytap-launch'),
        launchSpinner = launchForm.find('.skytap-spinner'),
        launchXHR;

    // Prepare UI
    launchSpinner.hide();

    // Set up click handler for button that allows learners to launch exercise environment
    launchButton.on('click', function(e) {
        e.preventDefault();

        var handlerUrl = runtime.handlerUrl(element, 'launch'),
            keyboardLayout = launchForm.find('select').val();

        if (launchXHR) {
            launchXHR.abort();
        }

        launchSpinner.show();
        launchButton.prop('disabled', true);

        launchXHR = $.post(handlerUrl, JSON.stringify(keyboardLayout))
            .success(function(response) {
                var url = response.sharing_portal_url;
                var sharingPortal = window.open(url, '_blank');
                if (sharingPortal === null) {
                    alert(
                        gettext("The browser's popup blocker prevented the exercise environment from being launched.")
                    );
                } else {
                    sharingPortal.focus();
                }
            })
            .error(function(jqXHR, textStatus, errorThrown) {
                var error;
                if (jqXHR.hasOwnProperty('responseJSON') && jqXHR.responseJSON.hasOwnProperty('error')) {
                    error = jqXHR.responseJSON.error;
                } else {
                    error = gettext('An unknown error occurred while launching.');
                }
                $('#skytap-error-message').text('Error: ' + error);
            })
            .complete(function() {
                launchSpinner.hide();
                launchButton.prop('disabled', false);
            });

    });

}
