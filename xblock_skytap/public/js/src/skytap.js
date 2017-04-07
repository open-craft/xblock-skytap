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

        launchXHR = $.post(handlerUrl, JSON.stringify(keyboardLayout))
            .success(function(response) {
                // FIXME: Open sharing portal link from response (OC-2505)
                var sharingPortal = window.open('https://www.skytap.com/', '_blank');
                if (sharingPortal === null) {
                    alert("The browser's popup blocker prevented the exercise environment from being launched.");
                } else {
                    sharingPortal.focus();
                }
            })
            .error(function(jqXHR, textStatus, errorThrown) {
                // FIXME: Display appropriate error message (OC-2505)
            });

    });

}
