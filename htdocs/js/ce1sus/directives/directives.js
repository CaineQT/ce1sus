/**
 * 
 */


app.directive("plainText", function() {
  
  return {
    restrict: "E",
    scope: {
      celsusText: "=text"
    },
    templateUrl: "pages/common/text.html",
    controller: function($scope){
      var tempArray = $scope.celsusText.split('\n');
      var textArray = [];
      angular.forEach(tempArray, function(item) {
        textArray.push({"line": item});
      });

      $scope.preparedCelsusText = textArray;
    }
  };
});

app.directive("userForm", function() {
  
  return {
    restrict: "E",
    scope: {
      user: "=user",
      editMode: "=edit",
      groups: "=groups"
    },
    templateUrl: "pages/common/directives/userform.html",
    controller: function($scope){
      $scope.generateAPIKey = function() {
        $scope.user.api_key = generateAPIKey();
      };
    }
  };
});

app.directive("groupForm", function() {
  
  return {
    restrict: "E",
    scope: {
      group: "=group",
      editMode: "=edit"
    },
    templateUrl: "pages/common/directives/groupform.html"
  };
});

app.directive("addRemTable", function() {
  
  return {
    restrict: "E",
    scope: {
      title: "@title",
      foo: "=foo", //group.children
      allItems: "=all", //groups
      route: "@route",
      owner: "=owner"
    },
    templateUrl: "pages/common/directives/addremtables.html",
    controller: function($scope, $log, $timeout, Restangular, messages){
      //Split the associdated ones and available ones (definition of remaining)
      $scope.remaining = angular.copy($scope.allItems);
      if ($scope.foo) {
        $scope.associated = $scope.foo;
      } else {
        $scope.associated = [];
      }
      $scope.setRemaining = function() {
        var index = 0;
        var items_to_remove = [];
        angular.forEach($scope.remaining, function(item) {
          // remove selected from the group
          if (item.identifier == $scope.owner.identifier) {
            items_to_remove.push(index);
          } else {
            if ($scope.associated.length > 0) {
              angular.forEach($scope.associated, function(associatedEntry) {
                var id1 = associatedEntry.identifier;
                var id2 = item.identifier;
                if (id1.toLowerCase() == id2.toLowerCase()){
                  items_to_remove.push(index);
                  
                }
                
              }, $log);
            } else {
              //restangularize object
              $scope.associated =  [];
            }
          }
          index++;
        }, $log);
        //sort array from big to log
        items_to_remove = items_to_remove.reverse();
        angular.forEach(items_to_remove, function(index){
          $scope.remaining.splice(index, 1);
        });
      };
      //wait till the object was rendered
      $timeout($scope.setRemaining);

      $scope.selected_accociated = [];
      $scope.selected_remaining = [];
      var original_associated = angular.copy($scope.associated);
      //make diff of the group and the children
      $scope.addRemTableRemove = function() {
        angular.forEach($scope.selected_accociated, function(removedItemId) {
          // remove selected from the group
          var index = 0;
          angular.forEach($scope.associated, function(associatedEntry) {
            if (removedItemId == associatedEntry.identifier){
              
              $scope.associated.splice(index, 1);
              Restangular.one($scope.owner.route, $scope.owner.identifier).one($scope.route, removedItemId).remove().then(function (item) {
                if (item) {
                  messages.setMessage({'type':'success','message':'Item sucessfully removed'});
                } else {
                  messages.setMessage({'type':'danger','message':'Unkown error occured'});
                }
                $scope.selected_accociated = [];
                $scope.selected_remaining = [];
              }, function (response) {
                $scope.remaining = angular.copy($scope.allItems);
                $scope.associated = original_associated;
                $scope.setRemaining();
                
                handleError(response, messages);
              });
              
            }
            index++;
          }, $log);
          
          //search for the group details
          angular.forEach($scope.allItems, function(itemEntry) {
            if (itemEntry.identifier == removedItemId){
              $scope.remaining.push(itemEntry);
            }
          }, $log);
          
          
        }, $log);
      };
      
      $scope.addRemTableAdd = function() {
        var original_associated = angular.copy($scope.associated);
        angular.forEach($scope.selected_remaining, function(addedItemID) {
          // remove selected from the group
          var index = 0;
          angular.forEach($scope.remaining, function(remEntry) {
            if (addedItemID == remEntry.identifier){
              $scope.remaining.splice(index, 1);
            }
            index++;
          }, $log);
          
          //append the selected to the remaining groups
          //check if there are children
          //search for the group details
          
          angular.forEach($scope.allItems, function(itemEntry) {
            if (itemEntry.identifier == addedItemID){
              
              
              $scope.associated.push(itemEntry);
              //derestangularize the element
              //foo as the owner is modified 
              Restangular.one($scope.owner.route, $scope.owner.identifier).all($scope.route).post({'identifier':itemEntry.identifier,'name':itemEntry.name}).then(function (item) {
                if (item) {
                  messages.setMessage({'type':'success','message':'Item sucessfully associated'});
                } else {
                  
                  messages.setMessage({'type':'danger','message':'Unkown error occured'});
                }
                $scope.selected_accociated = [];
                $scope.selected_remaining = [];
              }, function (response) {
                $scope.remaining = angular.copy($scope.allItems);
                $scope.associated = original_associated;
                $scope.setRemaining();
                
                handleError(response, messages);
              });
            }
          }, $log);
          
          
        }, $log);
        
      };
    }
  };
});

app.directive("objectDefinitionForm", function() {
  
  return {
    restrict: "E",
    scope: {
      object: "=object",
      editMode: "=edit"
    },
    templateUrl: "pages/common/directives/objectdefinitionform.html"
  };
});

app.directive("attributeDefinitionForm", function() {
  
  return {
    restrict: "E",
    scope: {
      attribute: "=attribute",
      editMode: "=edit",
      handlers: "=handlers",
      tables: "=tables",
      types: "=types",
      viewTypes: "=viewtypes",
      reset: "=doreset"
    },
    templateUrl: "pages/common/directives/attributedefinitionform.html",
    controller: function($scope, $log){
      $scope.available_tables = angular.copy($scope.tables);
      $scope.available_types = angular.copy($scope.types);
      $scope.available_viewTypes = angular.copy($scope.viewTypes);
      $scope.available_handlers = angular.copy($scope.handlers);
      
      $scope.handlerChange = function (){

        var handler_id = $scope.attribute.attributehandler_id;
        //keep only the ones usable in the table list
        angular.forEach($scope.handlers, function(itemEntry) {
          if (itemEntry.identifier == handler_id) {
            $scope.available_tables = itemEntry.allowed_tables;
          }
        }, $log);
        // Check if the there was previously an item selected and when check if it sill matches
        if ($scope.attribute.table_id) {
          var found = false;
          angular.forEach($scope.available_tables, function(itemEntry) {
            if (itemEntry.identifier == $scope.attribute.table_id) {
              found = true;
            }
          }, $log);
          if (!found) {
            delete $scope.attribute.table_id;
          }
        }
      };
      $scope.tableChange = function (){
        var table_id = $scope.attribute.table_id;
        newAvailableHandlers = [];
        //keep only the ones usable in the types list
        angular.forEach($scope.handlers, function(itemEntry) {
          angular.forEach(itemEntry.allowed_tables, function(allowed_table) {
            if (allowed_table.identifier == table_id) {
              newAvailableHandlers.push(itemEntry);
            }
          }, $log);
        }, $log);
        $scope.available_handlers = newAvailableHandlers;
        
        //remove the items which do not match
        var found = false;
        if ($scope.attribute.attributehandler_id) {
          found = false;
          angular.forEach($scope.available_handlers, function(itemEntry) {
            if (itemEntry.identifier == $scope.attribute.attributehandler_id) {
              found = true;
            }
          }, $log);
          if (!found) {
            delete $scope.attribute.attributehandler_id;
          }
        }
        
        newTypes = [];
        //keep only the ones usable in handlers list
        angular.forEach($scope.types, function(itemEntry) {
          if (itemEntry.allowed_table.identifier == table_id) {
            newTypes.push(itemEntry);
          } else {
            if (itemEntry.allowed_table.name == 'Any') {
              newTypes.push(itemEntry);
            }
          }
        }, $log);
        $scope.available_types = newTypes;
        
        //remove the items which do not match
        if ($scope.attribute.type_id) {
          found = false;
          angular.forEach($scope.available_types, function(itemEntry) {
            if (itemEntry.identifier == $scope.attribute.type_id) {
              found = true;
            }
          }, $log);
          if (!found) {
            delete $scope.attribute.type_id;
          }
        }
        
      };
      
      $scope.typeChange = function (){
        

        
      };
      

      

      $scope.$watch('reset', function(newValue, oldValue) {
        //would have preferred to call a function but this also works
        if (newValue) {
          $scope.available_tables = angular.copy($scope.tables);
          $scope.available_types = angular.copy($scope.types);
          $scope.available_viewTypes = angular.copy($scope.viewTypes);
          $scope.available_handlers = angular.copy($scope.handlers);
          
          delete $scope.attribute.viewType_id;
          delete $scope.attribute.table_id;
          delete $scope.attribute.type_id;
          delete $scope.attribute.attributehandler_id;
          $scope.reset=false;
        }
      });
      
    }
  };
});

app.directive("typeForm", function() {
  
  return {
    restrict: "E",
    scope: {
      type: "=type",
      datatypes: "=datatypes",
      editMode: "=edit"
    },
    templateUrl: "pages/common/directives/typeform.html"
  };
});

app.directive("viewtypeForm", function() {
  
  return {
    restrict: "E",
    scope: {
      viewType: "=viewtype",
      editMode: "=edit"
    },
    templateUrl: "pages/common/directives/viewtypeform.html"
  };
});




app.directive("composedobservable", function($compile) {
  
  return {
    restrict: "E",
    replace: true,
    transclude: true,
    scope: {
      composedobservable: "=composedobservable",
      indent: "=indent"
    },
    controller: function($scope, Pagination, $modal){
      $scope.pagination = Pagination.getNew(5,'composedobservable.observable_composition');
      $scope.pagination.numPages = Math.ceil($scope.composedobservable.observable_composition.observables.length/$scope.pagination.perPage);
      $scope.pagination.setPages();
      $scope.removeComposedObservable = function() {
        var remove = false;
        if (confirm('Are you sure you want to delete this composed observable?')) {
          if ($scope.composedobservable.observable_composition.observables.length > 0) {
            remove = confirm('Are you sure you want also it\'s children?');
          } else {
            remove = true;
          }
        }
        if (remove) {
          //find a way to make this more neat see $parent
          var index = $scope.$parent.observables.indexOf($scope.composedobservable);
          $scope.$parent.observables.splice(index,1);
        }
      };
      
      $scope.addObservable = function(){
        $modal({scope: $scope, template: 'pages/events/event/observable/add.html', show: true});
      };
      
      $scope.appendObservable =  function(observable){
        $scope.composedobservable.observable_composition.observables.push(observable);
      };
      
    },
    templateUrl: "pages/common/directives/composendobservableview.html",
    compile: function (element) {
      var contents = element.contents().remove();
      var compiled;
      return function(scope,element){
        if(!compiled)
            compiled = $compile(contents);
        
        compiled(scope,function(clone){
          element.append(clone);
            
        });
      };
    },
  };
});

app.directive("observable", function($compile) {
  
  return {
    restrict: "E",
    replace: true,
    transclude: true,
    scope: {
      observable: "=observable",
      indent: "=indent"
    },
    controller: function($scope, $modal, $log){
      
      
      
      $scope.getTitle = function(observable){
        if (observable.title){
          return observable.title;
        } else {
          return "Observable";
        }
      };
      
      $scope.editObservable = function(){
        $modal({scope: $scope, template: 'pages/events/event/observable/edit.html', show: true});
      };
      
      $scope.setObservable = function(observable){
        //TODO make this also work if the parent is not composed!
        var index = $scope.$parent.$parent.$parent.composedobservable.observable_composition.observables.indexOf($scope.observable);
        $scope.$parent.$parent.$parent.composedobservable.observable_composition.observables[index] = observable;
      };
      
      $scope.removeObservable = function(){
      //TODO make this also work if the parent is not composed!
        if (confirm('Are you sure you want to delete?')) {

          //TODO: find a way to do this more neatly see $parent.$parent.$parent, perhaps this changes!?
          var index = $scope.$parent.$parent.$parent.composedobservable.observable_composition.observables.indexOf($scope.observable);
          $scope.$parent.$parent.$parent.composedobservable.observable_composition.observables.splice(index,1);
          //foo to get the paginaton right in case it changes
          var oldnumPages = $scope.$parent.$parent.$parent.pagination.numPages;
          $scope.$parent.$parent.$parent.pagination.numPages = Math.ceil($scope.$parent.$parent.$parent.composedobservable.observable_composition.observables.length/$scope.$parent.$parent.$parent.pagination.perPage);
          if (oldnumPages != $scope.$parent.$parent.$parent.pagination.numPages) {
            $scope.$parent.$parent.$parent.pagination.setPages();
            if (oldnumPages < $scope.$parent.$parent.$parent.pagination.numPages) {
              $scope.$parent.$parent.$parent.pagination.nextPage();
            } else {
              $scope.$parent.$parent.$parent.pagination.prevPage();
            }
            
          }
          
          
        }
      };
      
      $scope.addObject = function(){
        $modal({scope: $scope, template: 'pages/events/event/observable/details.html', show: true});
      };
      
      $scope.showDetails = function(){
        $modal({scope: $scope, template: 'pages/events/event/observable/details.html', show: true});
      };
    },
    templateUrl: "pages/common/directives/observableview.html",
    compile: function(tElement, tAttr, transclude) {
      var contents = tElement.contents().remove();
      var compiledContents;
      return function(scope, iElement, iAttr) {

          if(!compiledContents) {
              compiledContents = $compile(contents, transclude);
          }
          compiledContents(scope, function(clone, scope) {
                   iElement.append(clone); 
          });
      };
    }
  };
});

app.directive("object", function($compile) {
  
  return {
    restrict: "E",
    replace: true,
    transclude: true,
    scope: {
      object: "=object",
      indent: "=indent"
    },
    controller: function($scope, $modal){
      $scope.showDetails = function(){
        $modal({scope: $scope, template: 'pages/events/event/observable/object/details.html', show: true});
      };
      $scope.removeObject = function(){
        if (confirm('Are you sure you want to delete this object?')) {
          var remove = false;
          if ($scope.object.relatedObjects) {
            remove = confirm('Are you sure you want also it\'s children?');
          } else {
            remove = true;
          }
          if (remove){
            //find a way to do this more neatly see $parent.$parent, perhaps this changes!?
            $scope.$parent.observable.object = null;
          }
        }
      };
      
      $scope.removeAttribute = function(attribtue){
        if (confirm('Are you sure you want to delete this attribtue?')) {
          var index = $scope.object.attributes.indexOf(attribtue);
          $scope.object.attributes.splice(index, 1);
        }
      };
      $scope.showAttributeDetails = function(attribtue){
        $scope.attribtueDetails = attribtue;
        $modal({scope: $scope, template: 'pages/events/event/observable/object/attributes/details.html', show: true});
      };
    },
    templateUrl: "pages/common/directives/objectview.html",
    compile: function(tElement, tAttr, transclude) {
      var contents = tElement.contents().remove();
      var compiledContents;
      return function(scope, iElement, iAttr) {

          if(!compiledContents) {
              compiledContents = $compile(contents, transclude);
          }
          compiledContents(scope, function(clone, scope) {
                   iElement.append(clone); 
          });
      };
    }
  };
});

app.directive("menu", function($compile, $timeout) {
  
  return {
    restrict: "E",
    transclude: true,
    replace: true,
    scope: {
      items: "=items",
      first: "=first",
      limit: "=limit"
    },
    controller: function($scope, $anchorScroll, $location){
      $scope.getTitle = function(observable){
        if (observable.observable_composition){
          return "Composed observable";
        } else {
            if (observable.title) {
              return observable.title;
            } else {
              if (observable.object) {
                return "Observable - "+ observable.object.definition.name;
              } else {
                return "Observable";
              }
              
            }
          
        }
      };
      
      $scope.scrollTo = function(id) {
        if ($location.hash() !== id) {
          var hash =  $location.hash(id);
        } else {
          $anchorScroll();
        }
      };
    },
    templateUrl: "pages/common/directives/menuitem.html",
    compile: function(tElement, tAttr, transclude) {
      var contents = tElement.contents().remove();
      var compiledContents;
      return function(scope, iElement, iAttr) {

          if(!compiledContents) {
              compiledContents = $compile(contents, transclude);
          }
          compiledContents(scope, function(clone, scope) {
                   iElement.append(clone); 
          });
      };
    }
  };
});

app.directive("observableForm", function() {
  
  return {
    restrict: "E",
    scope: {
      observable: "=observable",
      editMode: "=edit"
    },
    templateUrl: "pages/common/directives/observableform.html"
  };
});