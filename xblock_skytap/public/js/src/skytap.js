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

        console.log("Trying to launch exercise environment ...");

        var handlerUrl = runtime.handlerUrl(element, 'launch'),
            keyboardLayout = launchForm.find('select').val();

        console.log("handlerUrl: " + handlerUrl);
        console.log("keyboardLayout: " + keyboardLayout);

        if (launchXHR) {

            console.log("Aborting another launch that is currently in progress ...");

            launchXHR.abort();
        }

        console.log("Showing spinner ...");
        launchSpinner.show();

        console.log("Disabling 'Open' button ...");
        launchButton.prop('disabled', true);

        console.log("Sending launch request to server ...");

        launchXHR = $.post(handlerUrl, JSON.stringify(keyboardLayout))
            .success(function(response) {

                console.log("Launch successful.");
                console.log("Response:");
                console.log(response);

                console.log("Obtaining sharing portal URL ...");
                var url = response.sharing_portal_url;
                console.log("url: " + url);

                /*
                 The standard behaviour is to open the exercise environment in a new tab using a popup,
                 to allow the user to keep the course tab open too. However on iOS devices for example,
                 popups are blocked by default and the user is not informed that the popup failed to open.
                 Therefore for iOS devices a redirect is used instead. For consistency this is done for all
                 mobile devices.
                 */
                var isiOS = navigator.userAgent.match(/(iPod|iPhone|iPad)/i);
                var isAndroid = navigator.userAgent.match(/(android)/i);
                var isWindows = navigator.userAgent.match(/(Windows Phone|iemobile)/i);
                if (isiOS || isAndroid || isWindows) {
                    // Simply redirect for mobile devices.
                    console.log("Redirecting mobile device to sharing portal URL ...");
                    window.location = url;
                } else {
                    console.log("Opening sharing portal URL in new tab ...");
                    // Desktop browsers offer an easy way to allow the popup so being blocked is ok.
                    var sharingPortal = window.open(url, '_blank');
                    if (sharingPortal === undefined || sharingPortal === null) {
                        // Need to test for both null (from desktop browsers blocking the popup)
                        // and also undefined (from mobile Safari refusing to show the popup).
                        console.log("Could not open new tab.");
                        alert(gettext("The browser's popup blocker prevented the exercise environment from being launched."));
                    } else {
                        console.log("Focusing new tab ...");
                        sharingPortal.focus();
                    }
                }
            })
            .error(function(jqXHR, textStatus, errorThrown) {

                console.log("Launch unsuccessful.");
                console.log("jqXHR:");
                console.log(jqXHR);
                console.log("textStatus: " + textStatus);
                console.log("errorThrown: " + errorThrown);

                var error;
                if (jqXHR.hasOwnProperty('responseJSON') && jqXHR.responseJSON.hasOwnProperty('error')) {
                    console.log("Got a specific error message.");
                    error = jqXHR.responseJSON.error;
                } else {
                    console.log("Did not get a specific error message.");
                    error = gettext('An unknown error occurred while launching.');
                }

                console.log("Updating GUI with error message ...");
                $('#skytap-error-message').text('Error: ' + error);
            })
            .complete(function() {
                console.log("Hiding spinner ...");
                launchSpinner.hide();
                console.log("Enabling 'Open' button ...");
                launchButton.prop('disabled', false);
                console.log("DONE.");
            });

    });

}
