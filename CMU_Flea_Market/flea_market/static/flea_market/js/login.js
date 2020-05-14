var app = angular.module('mainModule', []);

app.controller('mainController', function($scope, $http) { //o scope liga o js e o template
  $scope.nome = 'Valor Inicial';
  //$http.get().success();
  $scope.reset = function()
  {
    $scope.nome = '';
  }
});

$(document).ready(function () {
  $(document).keyup(function(event){
    if(event.keyCode === 13){
      $("#login-button").trigger("click");
    }
  });
});
