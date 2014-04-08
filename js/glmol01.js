define(['GLmol'],function(d){
	if ( window.glmol === undefined ) {
		try{
			window.glmol = new GLmol('glmol01', true);
		}
		catch(e) {
			window.glmol = {
					loadMolecule: function(){},
					show: function(){},
					rebuildScene: function() {},
					get_selected_residue_numbers: function() {}
			};
		}
	}
	return window.glmol;
});