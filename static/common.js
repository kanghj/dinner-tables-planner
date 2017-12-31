$(document).ready(function() {
    $('form').submit(function(event) {
        $('form input[type="submit"]')
        .attr('disabled', 'disabled')
        .val('Submitting...');
    });
});

