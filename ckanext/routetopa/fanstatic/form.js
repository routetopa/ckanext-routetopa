function tetMetadataCompleness() {
	var inputs = $("#dataset-edit").find("input");
	var total = inputs.length - 3;
	var i =0,value =0, result =0;
	for (i=0; i < total ; i++){
		if ($(inputs[i]).val() != "") value += 1;
	}
	result = Math.round(value/total * 100);
	$(".bar").css("width", result+"%");
	$("#field-completeness").val(result)
}
$(document).ready(function () {
	tetMetadataCompleness();
    $("#dataset-edit").change(tetMetadataCompleness);
});