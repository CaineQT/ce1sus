/**
 * 
 */

app.controller("observableObjectAddController", function($scope, Restangular, messages, $routeSegment,$log) {
  $scope.definitions =[];
  Restangular.one("objectdefinition").getList(null, {"complete": true, "inflated": false}).then(function (objects) {
    $scope.definitions = objects;
  }, function(response) {
    handleError(response, messages);
    $scope.$hide();
  });
  
  var original_observableObject = {'properties' : {'shared': false},
                                   'definition_id': null};
  $scope.observableObject=angular.copy(original_observableObject);
  
  $scope.$watch(function() {
    return $scope.observableObject.definition_id;
    }, function(newVal, oldVal) {
      for (var i = 0; i < $scope.definitions.length; i++) {
        if ($scope.definitions[i].identifier === $scope.observableObject.definition_id){
          $scope.observableObject.properties.shared = $scope.definitions[i].default_share;
          break;
        }
      }
    });
  
  $scope.closeModal = function(){
    $scope.observableObject = angular.copy(original_observableObject);
    $scope.$hide();
  };
  
  //Scope functions
  $scope.resetObservableObject = function ()
  {
    $scope.observableObject = angular.copy(original_observableObject);

  };
  

  
  $scope.observableObjectChanged = function ()
  {
    return !angular.equals($scope.observableObject, original_observableObject);
  };
  
  $scope.submitObservableObject = function(){
    for (var i = 0; i < $scope.definitions.length; i++) {
      if ($scope.definitions[i].identifier == $scope.observableObject.definition_id){
        $scope.observableObject.definition=$scope.definitions[i];
        break;
      }
    }
    var observableID = $scope.$parent.$parent.observable.identifier;
    Restangular.one('observable', observableID).post('object', $scope.observableObject, {'complete':true, 'infated':true}).then(function (data) {
      $scope.$parent.appendObservableObject(data);
    }, function (response) {
      $scope.observableObject = angular.copy(original_observableObject);
      handleError(response, messages);
    });
    $scope.$hide();
  };


});


app.controller("objectChildAddController", function($scope, Restangular, messages, $routeSegment,$log) {
  $scope.definitions =[];
  Restangular.one("objectdefinition").getList(null, {"complete": true}).then(function (objects) {
    $scope.definitions = objects;
  }, function(response) {
    handleError(response, messages);
    $scope.$hide();
  });
  
  
  
  var original_relatedObject = {'object': {'definition_id': null, 'properties' : {'shared': false}}};
  $scope.relatedObject=angular.copy(original_relatedObject);

  $scope.$watch(function() {
    return $scope.relatedObject.object.definition_id;
    }, function(newVal, oldVal) {
      for (var i = 0; i < $scope.definitions.length; i++) {
        if ($scope.definitions[i].identifier === $scope.relatedObject.object.definition_id){
          $scope.relatedObject.object.properties.shared = $scope.definitions[i].default_share;
          break;
        }
      }
    });
  
  $scope.closeModal = function(){
    $scope.relatedObject = angular.copy(original_relatedObject);
    $scope.$hide();
  };
  
  //Scope functions
  $scope.resetrelatedObject = function ()
  {
    $scope.relatedObject = angular.copy(original_relatedObject);

  };
  

  
  $scope.relatedObjectChanged = function ()
  {
    return !angular.equals($scope.relatedObject, original_relatedObject);
  };
  
  $scope.submitrelatedObject = function(){
    for (var i = 0; i < $scope.definitions.length; i++) {
      if ($scope.definitions[i].identifier == $scope.relatedObject.definition_id){
        $scope.relatedObject.definition=$scope.definitions[i];
        break;
      }
    }
    var eventID = $routeSegment.$routeParams.id;
    if ($scope.$parent.$parent.object){
      //This is a child object
      $scope.relatedObject.parent_id=$scope.$parent.$parent.object.identifier;
    }
    var objectID = $scope.$parent.$parent.object.identifier;
    Restangular.one('object', objectID).post('related_object', $scope.relatedObject, {'complete':true, 'infated':true}).then(function (data) {
      if (!$scope.$parent.$parent.object.related_objects){
        $scope.$parent.$parent.object.related_objects = [];
      }
      $scope.$parent.$parent.object.related_objects.push(data);
    }, function (response) {
      handleError(response, messages);
    });
    $scope.$hide();
  };

});

app.controller("observableObjectPropertiesController", function($scope, Restangular, messages, $routeSegment,$log) {
  
  //set the id of the parent
  if (!$scope.object.parent_object_id) {
    $scope.object.parent_object_id = null;
  }
  if ($scope.object.parent_object_id) {
    Restangular.one("observable", $scope.object.observable_id).one("object").getList(null, {"complete": false, "flat": true}).then(function (objects) {
      $scope.objects = objects;
      //remove the object it self
      for (var i = 0; i < $scope.objects.length; i++) {
        if ($scope.objects[i].identifier == $scope.object.identifier){
          $scope.objects.splice(i,1);
          break;
        }
      }
      index = 0;
      /*
      //remove the parent object
      angular.forEach($scope.objects, function(entry) {
        if (entry.identifier == $scope.object.parent_object_id){
          $scope.objects.splice(index,1);
        }

        index++;
      }, $log);
      */
      Restangular.one('relations').getList().then(function(relations) {
        $scope.relations = relations;
      }, function(response) {
        handleError(response, messages);
        $scope.$hide();
      });
    }, function(response) {
      handleError(response, messages);
      $scope.$hide();
    });
  } else {
    $scope.objects = [];
  }
  
  $scope.get_name = function(object){
    if (object.identifier) {
      return object.definition.name + ' - '+object.identifier;
    } else {
      return object.definition.name;
    }
  };

  var original_object = angular.copy($scope.object);
  
  $scope.closeModal = function(){
    $scope.object = angular.copy(original_object);
    $scope.$hide();
  };
  
  //Scope functions
  $scope.resetObject = function ()
  {
    $scope.object = angular.copy(original_object);

  };
  

  
  $scope.objectChanged = function ()
  {
    return !angular.equals($scope.object, original_object);
  };
  
  $scope.submitObject = function(){
    //restangularize object
    restangularObject = Restangular.restangularizeElement(null, $scope.object, 'object');
    restangularObject.put({'complete':false, 'infated':false}).then(function (data) {
      $scope.$hide();
      if (original_object.parent_object_id != $scope.object.parent_object_id) {
        var length = $routeSegment.chain.length - 1;
        $routeSegment.chain[length].reload();
      }
    }, function (response) {
      handleError(response, messages);
      $scope.$hide();
    });
    
  };
});
