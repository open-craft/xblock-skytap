/* Javascript for SkytapXBlock. */

function SkytapXBlock(runtime, element) {
    "use strict";

    var activationForm = $('.skytap-activation-form', element),
        activateButton = activationForm.find('.skytap-activate'),
        launchForm = $('.skytap-launch-form', element),
        launchButton = launchForm.find('.skytap-launch');

    launchForm.hide();

    activateButton.on('click', function(e) {
        e.preventDefault();
        activationForm.hide();
        launchForm.show();
    });

}
