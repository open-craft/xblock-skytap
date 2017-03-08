/* Javascript for SkytapXBlock. */

function SkytapXBlock(runtime, element) {
    "use strict";

    var launchForm = $('.skytap-launch-form', element),
        launchButton = launchForm.find('.skytap-launch');

    launchButton.on('click', function(e) {
        e.preventDefault();
        var sharingPortal = window.open('https://www.skytap.com/', '_blank');
        sharingPortal.focus();
    });

}
