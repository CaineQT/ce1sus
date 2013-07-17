<%namespace name="inputBoxes" file="/components/inputBoxes.mako"/>

<%def name="userModal(id,label,user,showButtons=True,enabled=True, hide=True)">
    
    <div id="${id}" class="modal hide fade" tabidnex="-1" role="dialog" aria-labelledby="userModalLabel" aria-hidden="true">
        <div class="modal-header">
            <button type="button" class="close" onclick="window.location.href = window.location.protocol +'//'+ window.location.host + '/admin/users'">x</button>
            <h3 id="idLabel">${label}</h3>
        </div>
        <div class="modal-body">
            ${inputBoxes.userForm(user, enabled)}
        </div>
        <div class="modal-footer">
            % if showButtons:
                <button type="button" class="btn" onclick="window.location.href = window.location.protocol +'//'+ window.location.host + '/admin/users'">Close</button>
                <button class="btn btn-primary" type="submit">Save changes</button>
            % endif
        </div>
    </div>
    
     % if hide:
        <script>$("#${id}").modal('show');</script>
     % endif
</%def>

<%def name="groupModal(id,label,group,showButtons=True,enabled=True, hide=True)">
    
    <div id="${id}" class="modal hide fade" tabidnex="-1" role="dialog" aria-labelledby="userModalLabel" aria-hidden="true">
        <div class="modal-header">
            <button type="button" class="close" onclick="window.location.href = window.location.protocol +'//'+ window.location.host + '/admin/groups'">x</button>
            <h3 id="idLabel">${label}</h3>
        </div>
        <div class="modal-body">
           ${inputBoxes.groupForm(group, enabled)}
        </div>
        <div class="modal-footer">
            % if showButtons:
                <button type="button" class="btn" onclick="window.location.href = window.location.protocol +'//'+ window.location.host + '/admin/groups'">Close</button>
                <button class="btn btn-primary" type="submit">Save changes</button>
            % endif
        </div>
    </div>
    
     % if hide:
        <script>$("#${id}").modal('show');</script>
     % endif
</%def>

<%def name="genericModal(id,label,text,showButtons=True)">
    <div id="${id}" class="modal hide fade" tabidnex="-1" role="dialog" aria-labelledby="userModalLabel" aria-hidden="true">
        <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal" aria-hidden="true">x</button>
            <h3 id="idLabel">${label}</h3>
        </div>
        <div class="modal-body">
            ${text}
        </div>
        <div class="modal-footer">
            % if showButtons:
                <button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>
                <button class="btn btn-primary" type="submit">Save changes</button>
            % endif
        </div>
    </div>
</%def>