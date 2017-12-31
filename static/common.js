$(document).ready(function() {
    $('form:not(.download)').submit(function(event) {
        $('form input[type="submit"]')
        .attr('disabled', 'disabled')
        .val('Submitting...');
    });
});

