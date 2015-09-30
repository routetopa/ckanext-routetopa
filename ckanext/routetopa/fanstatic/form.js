$(document).ready(function () {
	$.getJSON( "/api/3/util/tet/getschema", function( data ) {
		var totalReq = 0, total = 0;
		$.each( data, function( key, val ) {
			if (val.required != undefined && val.required == "true") totalReq += 1;
			total +=1;
		    $("#dataset-edit").change(function (){
		    	reqComplete = 0, complete = 0, result = 0;
		    	$.each( data, function( key, val ) {
		    		if ($("#"+key).val() != "") {
		    			var item = data[$("#"+key).attr("id")];
		    			if (item != undefined && item.required != undefined && item.required == "true") reqComplete += 1;
		    			complete += 1;
		    		}
		    	});
		    	result = Math.round(complete/total * 100);
		    	if (reqComplete  < totalReq - 1 ) $(".progress").attr("class","progress progress-danger");
		    	else $(".progress").attr("class","progress progress-success");
		    	$(".bar").css("width", result+"%");
		    	$(".bar").text(result+"%");
		    	$("#field-completeness").val(result);
		    });
		    $("#field-completeness").change();
		});
    });
});