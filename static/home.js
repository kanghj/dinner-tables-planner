function statusChangeCallback(response) {
      $('#facebook_access_token').val(response.authResponse.accessToken);
      $('.retrieve-results').hide(); // a logged-in user directly uses the .existing-jobs div to retrieve
      $('.fb-logout').removeClass('hide');
      $('.fb-login-button').parent().addClass('hide');
      fetchExistingJobs(response.authResponse.accessToken);
}

function fetchExistingJobs(accessToken) {

  new Promise(function(resolve, reject) {
      $.get('/submissions_for_user?access_token=' + accessToken, function(response) {
            resolve(response);
      });
  }).then(function(response) {
      var responseNodes = $.parseHTML(response);
      var $responseNodes = $(responseNodes);
      $('.existing_jobs').replaceWith($responseNodes.filter('.existing_jobs')[0]);
  });

}