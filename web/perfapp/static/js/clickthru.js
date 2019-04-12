$(document).ready(function(){
  $('#clickable tr').click(function(){
    var n_href = $(this).find("a").attr("href")
    if (n_href) {
      window.location.href = href
    }
  })
});
