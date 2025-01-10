var hideIcon = function(cell, formatterParams, onRendered){ //plain text value
    return "<i class='fa fa-eye-slash'></i>";};


//--------------------------------------------------------

//toggle for table formatter
var tableToggleFormatter = function(cell, formatterParams){
	var self = this,
	el = $("<div class='tabulator-responsive-collapse-toggle'><span class='tabulator-responsive-collapse-toggle-open'>+</span><span class='tabulator-responsive-collapse-toggle-close'>-</span></div>");

	cell.getElement().addClass("tabulator-row-handle");

	//toggle table on click

	el.click(function(){
		var subTable = $(this).closest(".tabulator-row").find(".subtable-holder");

		$(this).toggleClass("open");
		
		if(subTable.hasClass("tabulator")){
			//remove table if it currently exists
			subTable.tabulator("destroy");
		}else{
			//create table if not present
			tableEl.tabulator({
				layout:"fitColumns",
				ajaxURL:"/getdatafromhere.com?id=" + cell.getData().id,
				columns:[
					{title:"Date", field:"date", sorter:"date"},
					{title:"Engineer", field:"engineer"},
					{title:"Action", field:"actions"},
				]
			})
		}
	});

	return el;
}

//table definition
$("#example-table").tabulator({
	height:"311px",
	layout:"fitColumns",
	resizableColumns:false,
	data:nestedData,
	columns:[
		{formatter:tableToggleFormatter, width:30, minWidth:30, align:"center", resizable:false, headerSort:false}, //toggle formatter
		{title:"Make", field:"make"},
		{title:"Model", field:"model"},
		{title:"Registration", field:"reg"},
		{title:"Color", field:"color"},
	],
	rowFormatter:function(row){
		//create holder element for table
		row.getElement().append("<div class='subtable-holder'></div>");
	},
})