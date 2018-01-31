$(document).ready(function() {
    $('form:not(.download)').submit(function(event) {
        $('form input[type="submit"]')
        .attr('disabled', 'disabled');
        $(event.target).find('input[type="submit"]')
        .val('Submitting...');

    });
     $('#see-original-clique-names').click(function(event) {
        $('.community-tag').toggleClass('show');
    });
});

/**
 * https://stackoverflow.com/questions/22889646/fb-getloginstatus-returns-status-unknown
 */
function deleteFbCookie(name) {
  document.cookie = name +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}
