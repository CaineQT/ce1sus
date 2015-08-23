/**
 * 
 */
app.controller("objectAttributeAddController", function($scope, Restangular, messages, $routeSegment,$log, $upload) {

  $scope.definitions =[];
  Restangular.one("objectdefinition", $scope.object.definition.identifier).getList("attributes",{"complete": true}).then(function (definitions) {
    $scope.definitions = definitions;
  }, function(response) {
    handleError(response, messages);
    $scope.$hide();
  });
  
  var original_attribute = {'properties' : {'shared': false},
                            'definition_id': null};
  $scope.attribute=angular.copy(original_attribute);
  
  $scope.closeModal = function(){
    $scope.attribute = angular.copy(original_attribute);
    $scope.$hide();
  };
  
  //Scope functions
  $scope.resetAttribute = function ()
  {
    $scope.attribute = angular.copy(original_attribute);

  };
  
  $scope.attributeChanged = function ()
  {
    return !angular.equals($scope.attribute, original_attribute);
  };
  
  $scope.submitAttribute = function(){
    for (var i = 0; i < $scope.definitions.length; i++) {
      if ($scope.definitions[i].identifier == $scope.attribute.definition_id){
        $scope.attribute.definition=$scope.definitions[i];
        break;
      }
    }
    var objectID = $scope.$parent.$parent.object.identifier;
    Restangular.one('object', objectID).post('attribute', $scope.attribute, {'complete':true, 'infated':true}).then(function (data) {
      $scope.$parent.appendData(data);
      
    }, function (response) {
      $scope.attribute = angular.copy(original_attribute);
      handleError(response, messages);
    });
    $scope.$hide();
  };


});

app.controller("objectAttributeEditController", function($scope, Restangular, messages, $routeSegment,$log, $upload) {
  $scope.definitions =[];
  
  var original_attribute = angular.copy($scope.attributeDetails);
  $scope.attribute=angular.copy(original_attribute);

  Restangular.one("objectdefinition", $scope.object.definition.identifier).getList("attributes",{"complete": true}).then(function (attributes) {
    $scope.definitions = attributes;
  }, function(response) {
    handleError(response, messages);
    $scope.$hide();
  });
  Restangular.one("condition").getList(null, {"complete": false}).then(function (conditions) {
    $scope.conditions = conditions;
  }, function(response) {
    handleError(response, messages);
    $scope.$hide();
  });
  $scope.closeModal = function(){
    $scope.attribute = angular.copy(original_attribute);
    $scope.$hide();
  };
  
  //Scope functions
  $scope.resetAttribute = function ()
  {
    $scope.attribute = angular.copy(original_attribute);

  };

  $scope.attributeChanged = function ()
  {
    return !angular.equals($scope.attribute, original_attribute);
  };
  

  
  

  
  $scope.submitAttribute = function(){
    for (var i = 0; i < $scope.definitions.length; i++) {
      if ($scope.definitions[i].identifier == $scope.attribute.definition_id){
        $scope.attribute.definition=$scope.definitions[i];
        break;
      }
    }
    var objectID = $scope.$parent.$parent.object.identifier;
    var restangularAttribute = Restangular.restangularizeElement(null, $scope.attribute, 'object/'+objectID+'/attribute');
    restangularAttribute.put({'complete':true, 'infated':true}).then(function (data) {
      $scope.$parent.updateAttribute(data);
    }, function (response) {
      $scope.attribute = angular.copy(original_attribute);
      handleError(response, messages);
    });
    $scope.$hide();
  };

  
});