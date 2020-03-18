$(document).ready(function(){
  var now = new Date();
  setInterval(function(){
    $.ajax({
      url: '/api/resturant/order/notification/' + now.toISOString() + '/',
      method: 'GET',
      success: function(data){
        if ((data['notification']) === 0){
          $('.badge').text('');
        }else{
          $('.badge').text(data['notification']);
        }
      }
    });
  }, 3000);
});
