function getPhotos(response) {
    if (response.status === 'connected') {
      new Promise(function(resolve, reject) {
          FB.api('/me', function(response) {
            var userId = response['id'];
            resolve(userId);
          });
      })
      .then(function(userId) {
        return new Promise(function(resolve, reject) {
            FB.api('/me/permissions/', function(response) {
                var declined = [];
                for (i = 0; i < response.data.length; i++) {
                    if (response.data[i].status == 'declined') {
                      declined.push(response.data[i].permission)
                    }
                }
                if (declined.length === 0)
                    resolve();
                else
                    reject();
            });
        });
      }).then(function() {
        fetchPhotos('/me/photos');
      }).catch(function(reason) {

      });

    } else {
      // not logged in
      document.getElementById('status').innerHTML = 'Please login to Facebook to use this feature. If you do not wish to initialise a template using your Facebook information, please directly download our template from the home page';
    }
    var accumulator = [];
    var userId;
    var persons = [];
    var person_ids = {};
    var communities = {};

    function fetchPhotos(next, response) {
        if (response) {
            for (data of response['data']) {
                accumulator.push(data);
            }
        }

        if (next) {
            FB.api(next, function(response) {
                if (!response.paging) {
                    return;
                }
                fetchPhotos(response.paging.next, response);
            });
        } else {
            fetchTaggedPeople(accumulator);
        }
    }

    function fetchTaggedPeople(photos) {
        var now = new Date();

        var i = 0;
        var retrievedPhotosPromises = [];
        for (photo of photos) {
            function fetchTagsForSinglePhoto(photo) {
                return new Promise(function(resolve, reject) {

                    FB.api(photo.id + '/tags', function(response) {
                        communities[photo.id] = [];
                        for (var data of response['data']) {
                            var name = data['name'];
                            if (data['name'] in person_ids && person_ids[data['name']] !== data['id']) {
                                name = data['name'] + '_' + data['id'];
                            }
                            person_ids[name] = data['id'];
                            persons.push(name);
                            communities[photo.id].push(persons.indexOf(name));

                        }

                        resolve();
                    });
                });
            }

            var photoDate = new Date(photo.created_time)

            var timeDiff = Math.abs(now.getTime() - photoDate.getTime());
            var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24));
            if (diffDays < (364 * 3) && i < 150) {
                retrievedPhotosPromises.push(fetchTagsForSinglePhoto(photo));
            }
            i += 1;
        }

        Promise
            .all(retrievedPhotosPromises)
            .then(requestSpreadsheet);
    }

    function requestSpreadsheet() {
        $('[name=communities]').val(JSON.stringify(communities));
        $('[name=persons]').val(JSON.stringify(persons));
        $('form').submit();
    }
}