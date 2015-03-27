/**
 * Main AngularJS Web Application
 */
var app = angular.module('collaborativeWebApp', ['ngRoute','angularModalService','ui.bootstrap','luegg.directives']);

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
	//fixed items for testing purposes:
	var item1 = {
			name: "Agenda",
			cost: 1,
			description:"Type your description here!"
	};
	var item2 = {
			name: "Item2",
			cost: 2,
			description:"Description 2"
	};
	var item3 = {
			name: "Spotlight",
			cost: 3,
			description:"Put yourself in the spotlight. On purchase you and your actions will be featured in the 'All Eyes On' window."
	};
	var item4 = {
			name: "Repay",
			cost: 4,
			description:"Be generous! \n Share your hard earned influence with the crowd. The cost of this item will be evenly distributed among your fellow gamers."
	};
	
	
	// ------------

	  var currentUser = {
			username: "J. Doe #" + Math.floor((Math.random() * 100) + 1),
	  		influence: 0,
	  		reputation: 0,
	  		achievements: [],
	  		availableItems:[item3, item4, item1] ,
	  		boughtItems:[],
	  		userFeatured: null,
	  		ws: new WebSocket("ws://" + window.location.host + "/ws?Id=123456789"),
	  		gamification : false,
	  		upvotesLeft: 0
	  };
	  return currentUser;
	});



/**
 * Controls all other Pages
 */
app.controller('PageCtrl', function (/* $scope, $location, $http */) {
  //console.log("Page Controller reporting for duty.");

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
		var types = ['success', 'warning', 'danger', 'info'];
		
        $scope.msgs = [];
        $scope.featuredUser = UserService.featuredUser;
        $scope.featuredmsg = null;
        $scope.inputText = "";
        $scope.author = UserService.username;
        $scope.upvotedAuthors = [];
        $scope.upvotesLeft = UserService.upvotesLeft;
        $scope.influence = UserService.influence;
        $scope.reputation = UserService.reputation;
    	$scope.voteOptions = [];
    	$scope.userVoted = null;
    	$scope.currentMode = null;
    	$scope.directInput = false;
    	$scope.userCommand = null;
    	
    	$scope.agendaVoted = true;
    	$scope.agendaText = "There is no current agenda";
    	$scope.agendaSuccessScore = 0;
    	$scope.agendaFailScore = 0;
    	$scope.agendaDenyScore = 0;
    	$scope.agendaSet = false;
    	
    	$scope.gamification = false;
    	
    	
    	$scope.latestAlert = null;
    	$scope.alerts = [];
    	//$scope.latestAlert = { type: 'success', msg: 'Congratulations! You have received your 50th upvote!' }
    	//$scope.alerts = [
    	//                   { type: 'danger', msg: 'Oh snap! Change a few things up and try submitting again.' },
    	//                  { type: 'success', msg: 'Well done! You successfully read this important alert message.' }
    	//                 ];
        //console.log("checkin " + $scope.author);
    	
    	 $scope.stacked = [{
	          value: 0,
	          type: types[0]
	        }, 
	        {
	            value: 0,
	            type: types[2]
	          },
	          {
	              value:0,
	              type: types[1]
	            }];
    	
        var init = false;
        var initialUsername = true;
       
        
    	$scope.activateDirectInputMode = function(){
    		console.log("direct input activated")
    		$scope.directInput = true;

    	}
    	$scope.deactivateDirectInputMode = function(){
    		console.log("direct input deactivated")
    		$scope.directInput = false;
    	}
    	
    	$scope.sendDirectInput = function($event) {
    		if ($scope.directInput){
    			//console.log(event)
    			if ($scope.userCommand == null){
    				$scope.userCommand = String.fromCharCode($event.keyCode);
    				//console.log(String.fromCharCode($event.keyCode));
    			}
    			UserService.ws.send(JSON.stringify(	{ message: String($event.which), author: UserService.username, time: (new Date()).toUTCString(), type:"keystroke"} ));
    		}
    		
    	}
    	
        $scope.submitVote = function () {
        	UserService.ws.send(JSON.stringify(	{ message: $scope.userVoted, author: UserService.username, time: (new Date()).toUTCString(), type:"modeVote"} ));
        };
        
        /** posting chat text to server */
        $scope.submitMsg = function () {
        	//console.log($scope.voteOptions);
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
    	    	  if (result.name !== null){
      	    	  	if (!initialUsername){
    	    	  		UserService.ws.send(JSON.stringify(	{ message: result.name, author: UserService.username, time: (new Date()).toUTCString(), type:"changeUser"} ));
    	    	  		UserService.username = result.name;
    	    	  	} else {
    	    	  		UserService.username = result.name;
    	    	  		UserService.ws.send(JSON.stringify(	{ message: UserService.username, author: UserService.username, time: (new Date()).toUTCString(), type:"newUser"} ));
    	    	  		initialUsername = false;
    	    	  	}
    	    	  	
    	    	  	
            		//always feature yourself next after introduction- remove this later
            		//UserService.userFeatured = UserService.username;
            		//UserService.ws.send(JSON.stringify(	{ message: UserService.username, author: UserService.username, time: (new Date()).toUTCString(), type:"featureUser"} ));
    	    	  	
    	    	  }

        		
    	      });
    	    });
        	//console.log(init)
        	if (!init){

        		//console.log(UserService.userFeatured)
        		init = true;
        		UserService.ws.send(JSON.stringify(	{ message: "", author: UserService.username, time: (new Date()).toUTCString(), type:"voteRequest"} ));
        		UserService.ws.send(JSON.stringify(	{ message: "", author: UserService.username, time: (new Date()).toUTCString(), type:"gamificationRequest"} ));
        	}
    	  };
    	  
        $scope.showShop = function() {
      	    ModalService.showModal({
      	      templateUrl: "web/partials/shop.html",
      	      controller: "ShopController",
      	      windowClass: 'right-modal',
      	      inputs: {
      	        title: "Shop 'til you drop!",
      	        items: UserService.availableItems,
      	        influence: UserService.influence
      	      }
      	    }).then(function(modal) {
      	      modal.element.modal();
      	      modal.close.then(function(result) {
      	    	  //console.log(result.chosen);
      	    	  if(result.chosen){
      	    		  	UserService.ws.send(JSON.stringify(	{ message: JSON.stringify(result.chosen), author: UserService.username, time: (new Date()).toUTCString(), type:"purchase"} ));
              	    	UserService.boughtItems.push(result.chosen);
      	    	  }

      	      });
      	    });
      	  };
      	  
      	  $scope.showNotifications = function() {
        	    ModalService.showModal({
            	      templateUrl: "web/partials/notifications.html",
            	      controller: "NotificationController",
            	      windowClass: 'right-modal',
            	      inputs: {
            	        title: "Recent Notifications",
            	        alerts: $scope.alerts
            	      }
            	    }).then(function(modal) {
            	      modal.element.modal();
            	      modal.close.then(function(result) {
            	    	  //console.log(result.chosen);
            	    	  $scope.alerts = result.alerts;
            	    	  });

            	      });
            	    };
    	  
    	$scope.upvoteMsg = function (msg) {
          	UserService.ws.send(JSON.stringify(	{ message: msg.author, author: UserService.username, time: (new Date()).toUTCString(), type:"upvoteMsg"} ));
          	$scope.upvotedAuthors.push(msg.author);
          	UserService.upvotesLeft = UserService.upvotesLeft-1;
          };
          
          
      	$scope.agendaSuccess = function () {
          	UserService.ws.send(JSON.stringify(	{ message: "agendaSuccess", author: UserService.username, time: (new Date()).toUTCString(), type:"agendaSuccess"} ));
          	$scope.agendaVoted = true;
          };
      	$scope.agendaFail = function () {
          	UserService.ws.send(JSON.stringify(	{ message: "agendaFail", author: UserService.username, time: (new Date()).toUTCString(), type:"agendaFail"} ));
          	$scope.agendaVoted = true;
          };
      	$scope.agendaDeny = function () {
          	UserService.ws.send(JSON.stringify(	{ message: "agendaDeny", author: UserService.username, time: (new Date()).toUTCString(), type:"agendaDeny"} ));
          	$scope.agendaVoted = true;
          };
          
        $scope.setAgenda = function (agenda){
        	$scope.agendaVoted = false;
        	$scope.agendaText = agenda.text;
        	$scope.agendaSuccessScore = 0;
        	$scope.agendaFailScore = 0;
        	$scope.agendaDenyScore = 0;
        	$scope.agendaSet = true;
        };
        
        $scope.updateAgenda = function (agenda){
        	if (!$scope.agendaSet){
        		$scope.agendaVoted = false;
            	$scope.agendaText = agenda.text;
            	$scope.agendaSet = true;
        	}
        	$scope.agendaSuccessScore = agenda.success;
        	$scope.agendaFailScore = agenda.fail;
        	$scope.agendaDenyScore = agenda.deny;
        	$scope.stacked[0].value = agenda.success;
        	$scope.stacked[1].value = agenda.fail;
        	$scope.stacked[2].value = agenda.deny;
        };
        
        $scope.finishAgenda = function (){
        	$scope.agendaVoted = true;
        	$scope.agendaText = "There is no current agenda";
        	$scope.agendaSuccessScore = 0;
        	$scope.agendaFailScore = 0;
        	$scope.agendaDenyScore = 0;
        	$scope.stacked[0].value = 0;
        	$scope.stacked[1].value = 0;
        	$scope.stacked[2].value = 0;
        	$scope.agendaSet = false;
        } ;
        
          
        $scope.addAlert = function(alert) {
        	    $scope.alerts.push(JSON.parse(alert));
        	    $scope.latestAlert = JSON.parse(alert);
        	  };

        $scope.closeAlert = function(index) {
        	    $scope.alerts.splice(index, 1);
        	  };
        $scope.dismissAlert = function(){
        	$scope.latestAlert = null;
        }
          
        /** handle incoming messages: add to messages array */
        UserService.ws.onmessage = function (msg) {
        	$scope.$apply(function (){
        		//console.log(msg);
        	if (JSON.parse(msg.data).type == "chatMsg" || JSON.parse(msg.data).type == "commandResult" ){
        		$scope.msgs.push(JSON.parse(msg.data));
        		if(JSON.parse(msg.data).author == UserService.userFeatured){
        			$scope.featuredmsg = JSON.parse(msg.data);
        		}
        		if (JSON.parse(msg.data).type == "commandResult"){
        			$scope.userCommand = null;
        		}
        		//console.log(msg);
        		//console.log("Featured: "+ $scope.featuredUser + " with message " + $scope.featuredmsg.message + " || In User Service: " + UserService.userFeatured + " || This author: " + msg.data.author);
        		//console.log(msg.data.author == UserService.userFeatured);
        	} 

            else if (JSON.parse(msg.data).type == "voteOption"){
            	$scope.voteOptions.push(JSON.parse(msg.data).message);}
            else if (JSON.parse(msg.data).type == "enableGamification"){
            	UserService.gamification = true;
            	console.log($scope.gamification);}
        	
            else if(JSON.parse(msg.data).type == "setAgenda"){
            	$scope.setAgenda(JSON.parse(JSON.parse(msg.data).message)) ;}
            else if(JSON.parse(msg.data).type == "updateAgenda"){
            	$scope.updateAgenda(JSON.parse(JSON.parse(msg.data).message)) ;}
            else if(JSON.parse(msg.data).type == "finishAgenda"){
            	$scope.finishAgenda() ;
            	$scope.addAlert(JSON.parse(msg.data).message);}        	
        	
            else if(JSON.parse(msg.data).type == "modeResult"){
            	$scope.currentMode = JSON.parse(msg.data).message;}
        	else if(JSON.parse(msg.data).type == "featureUser"){
        		UserService.userFeatured = JSON.parse(msg.data).message;}
        	else if (JSON.parse(msg.data).type == "updateUser"){
        		UserService.influence = JSON.parse(msg.data).influence;
        		UserService.reputation = JSON.parse(msg.data).reputation;
        	}
        	else if (JSON.parse(msg.data).type == "userAlert" || JSON.parse(msg.data).type == "globalAlert"){
        		$scope.addAlert(JSON.parse(msg.data).message);
        	}
        	else if (JSON.parse(msg.data).type == "refreshUpvotes"){
        		UserService.upvotesLeft = JSON.parse(msg.data).message;
        		$scope.upvotedAuthors = [];}       	
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
        $scope.$watch( function () { return UserService.userFeatured; }, function ( usr ) {
      	  // handle it here:
      	  $scope.featuredUser = usr;
      	});
        
        $scope.$watch( function () { return UserService.upvotesLeft; }, function ( upvotesLeft ) {
      	  // handle it here:
      	  $scope.upvotesLeft = upvotesLeft;
      	});
        
        $scope.$watch( function () { return UserService.gamification; }, function ( gamification ) {
        	  // handle it here:
        	  $scope.gamification = gamification;
        	});
        

    });

//Modal Controllers
//Username Menu
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
			name: null,
			age: $scope.age
			}, 500); // close, but give 500ms for bootstrap to animate
		};
}]);

//Shop
app.controller('ShopController', ['$scope', '$element', 'title', 'items', 'influence', 'close',
                                 	function($scope, $element, title, items, influence, close) {
                                 		$scope.items = items;
                                 		$scope.title = title;
                                 		$scope.influence = influence;
                                 		$scope.chosen = null
                                 		// This close function doesn't need to use jQuery or bootstrap, because
                                 		// the button has the 'data-dismiss' attribute.
                                 		$scope.close = function(item) {
                                 			close({
                                 			chosen: item,
                                 			}, 500); // close, but give 500ms for bootstrap to animate
                                 			};
                                 			// This cancel function must use the bootstrap, 'modal' function because
                                 			// the doesn't have the 'data-dismiss' attribute.
                                 			$scope.cancel = function(item) {
                                 			// Manually hide the modal.
                                 			$element.modal('hide');
                                 			// Now call close, returning control to the caller.
                                 			close({
                                 			chosen: item,
                                 			}, 500); // close, but give 500ms for bootstrap to animate
                                 		};
                                 }]);

app.controller('NotificationController', ['$scope', '$element', 'title', 'alerts', 'close',
                               	function($scope, $element, title, alerts, close) {
                               		$scope.alerts = alerts;
                               		$scope.title = title;
                                    $scope.closeAlert = function(index) {
                                	    $scope.alerts.splice(index, 1);
                                	  };
                                	$scope.dismissAll = function(){
                                		$scope.alerts = [];
                                	}
                               		// This close function doesn't need to use jQuery or bootstrap, because
                               		// the button has the 'data-dismiss' attribute.
                               		$scope.close = function() {
                               			close({
                               			alerts: $scope.alerts,
                               			}, 500); // close, but give 500ms for bootstrap to animate
                               			};
                               			// This cancel function must use the bootstrap, 'modal' function because
                               			// the doesn't have the 'data-dismiss' attribute.
                               			$scope.cancel = function(item) {
                               			// Manually hide the modal.
                               			$element.modal('hide');
                               			// Now call close, returning control to the caller.
                               			close({
                               			alerts: $scope.alerts,
                               			}, 500); // close, but give 500ms for bootstrap to animate
                               		};
                               }]);

app.controller('ProgressDemoCtrl', function ($scope) {
	var types = ['success', 'warning', 'danger', 'info'];
	  $scope.max = 200;
	  $scope.stacked = [{
	          value: 15,
	          type: types[0]
	        }, 
	        {
	            value: 20,
	            type: types[2]
	          },
	          {
	              value:17,
	              type: types[1]
	            }];
	          

	});
