function getCookie(cookieName) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, cookieName.length + 1) === (cookieName + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(cookieName.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function findElement(arr, propName, propValue) {
    for (var i=0; i < arr.length; i++)
      if (arr[i][propName] == propValue)
        return arr[i];
  
    // will return undefined if not found; you could return a default instead
  }