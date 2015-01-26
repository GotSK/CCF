/**
 * Main AngularJS Web Application
 */
var app = angular.module('tutorialWebApp', ['ngRoute','angularModalService']);

//author = "J. Doe #" + Math.floor((Math.random() * 100) + 1);
/**
 * Configure the Routes
 */
app.config(['$routeProvider', function ($routeProvider) {
  $routeProvider
    // Home
    .when("/", {templateUrl: "web/partials/home.html" , controller: "PageCtrl"})
    // Pages
    .when("/about", {templateUrl: "web/partials/about.html", controller: "PageCtrl"})
    .when("/faq", {templateUrl: "web/partials/faq.html", controller: "PageCtrl"})
    .when("/pricing", {templateUrl: "web/partials/pricing.html", controller: "PageCtrl"})
    .when("/services", {templateUrl: "web/partials/services.html", controller: "PageCtrl"})
    .when("/contact", {templateUrl: "web/partials/contact.html", controller: "PageCtrl"})
    // Blog
    .when("/blog", {templateUrl: "web/partials/blog.html", controller: "BlogCtrl"})
    .when("/blog/post", {templateUrl: "web/partials/blog_item.html", controller: "BlogCtrl"})
    // else 404
    .otherwise("/404", {templateUrl: "web/partials/404.html", controller: "PageCtrl"});
}]);

app.factory( 'UserService', function() {
	  var currentUser = {
			username: "J. Doe #" + Math.floor((Math.random() * 100) + 1),
	  		influence: 0,
	  		reputation: 5,
	  		achievements: [],
	  		ws: new WebSocket("ws://" + window.location.host + "/ws?Id=123456789")
	  };
	  return currentUser;
	});


/**
 * Controls all other Pages
 */
app.controller('PageCtrl', function (/* $scope, $location, $http */) {
  console.log("Page Controller reporting for duty.");

  // Activates the Carousel
  $('.carousel').carousel({
    interval: 5000
  });

  // Activates Tooltips for Social Links
  $('.tooltip-social').tooltip({
    selector: "a[data-toggle=tooltip]"
  })
});

  //Controls the chat
app.controller('ChatCtrl', function ($scope, $http, ModalService, UserService) {
        $scope.msgs = [];
        $scope.inputText = "";
        $scope.author = UserService.username;
        $scope.upvotedAuthors = [];
        $scope.influence = UserService.influence;
        $scope.influence = UserService.reputation;
    	$scope.voteOptions = [];
    	$scope.userVoted = null;
    	$scope.currentMode = null;
    	
        //console.log("checkin " + $scope.author);
        var init = false;
        $scope.submitVote = function () {
        	UserService.ws.send(JSON.stringify(	{ message: $scope.userVoted, author: UserService.username, time: (new Date()).toUTCString(), type:"modeVote"} ));
        };
        
        /** posting chat text to server */
        $scope.submitMsg = function () {
        	console.log($scope.voteOptions);
        	UserService.ws.send(JSON.stringify(	{ message: $scope.inputText, author: UserService.username, time: (new Date()).toUTCString(), type:"chatMsg"} ));
            $scope.inputText = "";
        };
        
        $scope.showComplex = function() {
    	    ModalService.showModal({
    	      templateUrl: "web/partials/loginmodal.html",
    	      controller: "ComplexController",
    	      windowClass: 'right-modal',
    	      inputs: {
    	        title: "Pick a Username!"
    	      }
    	    }).then(function(modal) {
    	      modal.element.modal();
    	      modal.close.then(function(result) {
    	    	UserService.username = result.name;
    	      });
    	    });
        	console.log(init)
        	if (!init){
        		init = true;
        		UserService.ws.send(JSON.stringify(	{ message: "", author: UserService.username, time: (new Date()).toUTCString(), type:"voteRequest"} ));
        	}
    	  };
    	  
    	$scope.upvoteMsg = function (msg) {
          	UserService.ws.send(JSON.stringify(	{ message: msg.author, author: UserService.username, time: (new Date()).toUTCString(), type:"upvoteMsg"} ));
          	$scope.upvotedAuthors.push(msg.author);
          };
          
        /** handle incoming messages: add to messages array */
        UserService.ws.onmessage = function (msg) {
        	$scope.$apply(function (){
        	if (JSON.parse(msg.data).type == "chatMsg" ){
        		$scope.msgs.push(JSON.parse(msg.data));} 
            else if (JSON.parse(msg.data).type == "voteOption"){
            	$scope.voteOptions.push(JSON.parse(msg.data).message);}
            else if(JSON.parse(msg.data).type == "modeResult"){
            	$scope.currentMode = JSON.parse(msg.data).message;}
                   	
        	})};
        
        $scope.$watch( function () { return UserService.username; }, function ( username ) {
        	  // handle it here:
        	  $scope.author = username;
        	});
        $scope.$watch( function () { return UserService.influence; }, function ( influence ) {
      	  // handle it here:
      	  $scope.influence = influence;
      	});
        $scope.$watch( function () { return UserService.reputation; }, function ( reputation ) {
        	  // handle it here:
        	  $scope.reputation = reputation;
        	});
        

    });

//Modal Controller
app.controller('ComplexController', ['$scope', '$element', 'title', 'close',
	function($scope, $element, title, close) {
		$scope.name = null;
		$scope.age = null;
		$scope.title = title;
		// This close function doesn't need to use jQuery or bootstrap, because
		// the button has the 'data-dismiss' attribute.
		$scope.close = function() {
			close({
			name: $scope.name,
			age: $scope.age
			}, 500); // close, but give 500ms for bootstrap to animate
			};
			// This cancel function must use the bootstrap, 'modal' function because
			// the doesn't have the 'data-dismiss' attribute.
			$scope.cancel = function() {
			// Manually hide the modal.
			$element.modal('hide');
			// Now call close, returning control to the caller.
			close({
			name: $scope.name,
			age: $scope.age
			}, 500); // close, but give 500ms for bootstrap to animate
		};
}]);