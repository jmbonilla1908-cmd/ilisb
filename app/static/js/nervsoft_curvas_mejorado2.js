var x=$(document);
x.ready(inicializar);

var flagNFF=0;

var puntos_calculados=[];

var puntos_a_procesar=[];
var puntos_procesados=[];

var puntero_entrada=0;

/*VARIABLES PARA GENERAR GRAFICO FINAL*/
var limitesObjeto={
	limites_graf:{
		x:{min:0,max:0},
		y:{min:0,max:0}
	},
	limites_visuales_graf:{
		x:{min:0,max:0},
		y:{min:0,max:0}
	}
}
	
var scatterChartData = {
	datasets: [
		{
			label: 'Curva de bomba',
			borderColor: window.chartColors.blue,
			backgroundColor: color(window.chartColors.red).alpha(0.2).rgbString(),
			//data: datosCurvaBomba.coord,
			data: null,
			pointRadius: 0, //TBR
			showLine: true, // TBR
			fill: false, //TBR
			hidden: false,
			borderWidth:1,
		},
		{
			label: 'Curva de bomba (frecuencia actualizable)',
			borderColor: window.chartColors.red,
			backgroundColor: color(window.chartColors.red).alpha(0.2).rgbString(),
			//data: datosCurvaBombaActualizable.coord,
			data: null,
			pointRadius: 0, //TBR
			showLine: true, // TBR
			fill: false, //TBR
		},
		{
			label: 'curva 1 de sistema',
			borderColor: window.chartColors.orange,
			backgroundColor: color(window.chartColors.red).alpha(0.2).rgbString(),
			//data: datosCurvaSistema1.coord,
			data: null,
			pointRadius: 0, //TBR
			showLine: true, // TBR
			fill: false, //TBR
			borderWidth:1,
		},
		{
			label: 'curva 2 de sistema',
			borderColor: window.chartColors.green,
			backgroundColor: color(window.chartColors.red).alpha(0.2).rgbString(),
			//data: datosCurvaSistema2.coord,
			data: null,
			pointRadius: 0, //TBR
			showLine: true, // TBR
			fill: false, //TBR
			
		},			
		{
			label: 'curva 3 de sistema',
			borderColor: window.chartColors.yellow,
			backgroundColor: color(window.chartColors.red).alpha(0.2).rgbString(),
			//data: datosCurvaSistema3.coord,
			data: null,
			pointRadius: 0, //TBR
			showLine: true, // TBR
			fill: false, //TBR
			borderWidth:1,
		},			
		{
			label: 'Puntos ingresados',
			borderColor: window.chartColors.gray,
			backgroundColor: color(window.chartColors.gray).alpha(0.2).rgbString(),
			//data:datosPuntos,
			data:null,
			//pointRadius: 0.5, //TBR
			showLine: false, // TBR
			fill: false, //TBR
		},
		{
			label: 'Interseccion',
			borderColor: window.chartColors.red,
			backgroundColor: color(window.chartColors.red).alpha(1).rgbString(),
			//data:datosInterseccion,
			data:null,
			pointRadius: 5, //TBR
			showLine: false, // TBR
			fill: false, //TBR
			//hidden: flagHiddenIntersection,
		},	
		{
			label: 'Curva de puntos',
			borderColor: window.chartColors.purple,
			backgroundColor:  window.chartColors.lightgreen,
			//backgroundColor: color(window.chartColors.red).alpha(0.2).rgbString(),
			//data: datosCurvaBomba.coord,
			data:null,
			pointRadius: 3, //TBR
			showLine: false, // TBR
			fill: false, //TBR
			//hidden: flagHiddenIntersection,
		},
		{
			label: 'Curva de puntos procesados',
			borderColor: window.chartColors.purple,
			backgroundColor: color(window.chartColors.red).alpha(0.2).rgbString(),
			//data: datosCurvaBomba.coord,
			data: null,
			pointRadius: 0, //TBR
			showLine: true, // TBR
			fill: false, //TBR
			hidden: false,
			borderWidth:2,
		},
	]
};

var configuracionGrafico={
	type: 'scatter',
	data: scatterChartData,
	options: {
				animation: {
					duration: 500,
				},
				responsive: true,
				maintainAspectRatio:true,
				title: {
					display: false,
					text: "title"
				},
				scales: {
					xAxes: [{
						grid: {
								  display: true,
								  drawBorder: true,
								  drawOnChartArea: true,
								  drawTicks: false,
							},
						/*								
						ticks: {
							min: limites_graf.x.min,
							max: limites_graf.x.max,
							//stepSize: 10,
							callback: function(val, index) {
								return index % 2 === 0 ? val : '';
							  },
						},	*/				
					}],
					yAxes: [
						{
						grid: {
								  display: true,
								  drawBorder: true,
								  drawOnChartArea: true,
								  drawTicks: false,
							},	
						
						/*
						ticks: {
							min: 0,
							max: limites_visuales_graf.y.max,
						}
						*/
					}]
				},
				legend: {
					display: false
				},
				tooltips: {
					callbacks: {
					   label: function(tooltipItem) {
							  return tooltipItem.yLabel;
					   }
					}
				}
			}


};

var scatterData=[
{},//datosCurvaBomba.coord
{},//datosCurvaBombaActualizable.coord;
{},//datosCurvaSistema1.coord;
{},//datosCurvaSistema2.coord;
{},//datosCurvaSistema3.coord;
{},//datosPuntos;
{},//datosInterseccion
{},//datosdesdepuntos
{}//datosdesdepuntosconvertidos
];

/*--VARIABLES PARA GENERAR GRAFICO FINAL*/

var clickHandler = ('ontouchstart' in document.documentElement ? "touchstart" : "click");

function inicializar(){
	console.log('->inicializar');
	
	inicializar_base();
	
	var anchoDispositivo=$("body").outerWidth();
	if (anchoDispositivo>500){
		anchoDispositivo=375;
	}
	
	$("#frame_grafico").css({"height":$("#frame_grafico").width()+"px"});
	$("#canvas").height($("#frame_grafico").width());
	$("#canvas").width($("#frame_grafico").width());
	
	$("body").on(clickHandler,"#arrow_next:not(.off)",arrow_next);	
	$("body").on(clickHandler,"#arrow_prev:not(.off)",arrow_prev);	
	$("body").on(clickHandler,"#borrar_punto:not(.off)",borrar_punto);	
	
	$("select[name='exponente'] option:last-child").prop("checked",true);
	
	$("input[name='radio_tipo_curva']").eq(0).prop("checked",true);
	
	$("#alert_box a.boton.answer").on(clickHandler,function(e){
		if($("#alert_box").attr("data-rel")=="verificacion_de_curva"){
			swipe(1);			
		}
		$("#alert_box").attr("data-rel","");

	});
	
	/*
	if(localStorage.hasOwnProperty('ilisb_curvas')){
		console.log("->localStorage.hasOwnProperty('ilisb_curvas')");
		var ilisb_curvas=localStorage.getItem("ilisb_curvas");
		console.log("localStorage[\"ilisb_curvas\"]");
		//console.log(localStorage["ilisb_curvas"]);
		console.log(JSON.parse(localStorage["ilisb_curvas"]));
		
		$.each(JSON.parse(localStorage["ilisb_curvas"]), function( index, value ) {
		  //console.log( typeof(value) );
			$("#datos_Q_H .bloque_input_puntos").removeClass("none");
			
			if(typeof(value)=="object"){
				//var orden=0;
				$.each(value, function( indexs, values ) {
					//console.log( indexs + ": " + values );	
					
					if($("input[name='"+index+"']").eq(indexs).length){
						$("input[name='"+index+"']").eq(indexs).val(values);
					}else{
						//console.log(":'(");
						var campos=$("<div class=\"bloque_input_puntos\"> <div class=\"espacio_boton\"> </div> <div class=\"input_puntos\"> <input type=\"number\" step=\"any\" name=\"Q[]\" required=\"\" value=\"\" class=\"ingreso_Q_H\"> </div>  <div class=\"input_puntos\"> <p><input type=\"number\" step=\"any\" name=\"H[]\" required=\"\" value=\"\" class=\"ingreso_Q_H\"></p> </div> <div class=\"espacio_boton\"> </div> </div>");
						$("#datos_Q_H").append(campos);
						$("#DIV_remove_Q_H").removeClass("none");
						
						$("input[name='"+index+"']").eq(indexs).val(values);
					}
				});			
			}else{
				//console.log( index + ": " + value );
				if($("input[name='"+index+"']").length){
					$("input[name='"+index+"']").val(value);
				}else if($("select[name='"+index+"']").length){
					//console.log("its select");
					$("select[name='"+index+"'] option[value='"+value+"']").attr("selected", true);
				}
				
			}
			
			$("#primer_uso").addClass("none");
			$("#continuar_2tab").removeClass("none");
			

		});
		actualizarNivelAguaSuccion();
		actualizarUnidMedidas();
		//revisar_precision();
		generarPrevista();
		$("#loading").fadeOut();
		
	}else{
		console.log("no hay local storage");
		$("#loading").addClass("none");
	}
	*/
	/*interfaces*/
	
	/*
	input_puntos_w=(anchoDispositivo-20-120-20-10)/2;
	$(".input_puntos").css({"width":input_puntos_w+"px"});
	*/
	
	$("#loading").fadeOut();
	
	$("#ajustes_boton").css({"right":"-100px"}).addClass("none");
	
	
	var label_caudal=[
	"",
	"[m3/h]",
	"[l/s]",
	"[GPM]"
	];
	
	var label_presion=[
	"",
	"[m]",
	"[PSI]",
	"[Bar]",
	"[Pies]",
	"[mm Hg]",
	"[Pulg Hg]",
	"[kPa]",
	"[Pa]"
	];	
	
	var label_diametro=[
	"",
	"[mm]",
	"[pulg]",
	"[Pies]"
	];		
	
	var label_distancia=[
	"",
	"[m]",
	"[Km]",
	"[pulg]",
	"[pies]"
	];		
	
	$("body").on("click","label.clickeable",function(){
		console.log($(this).attr("data-medida"));
		var datamedida=$(this).attr("data-medida");
		if(datamedida!="undefined"){
			var datarel=$(this).attr("data-rel");
			if(typeof(datarel)!="undefined"){
				if(datamedida=="caudal"){
					array=label_caudal;
				}else if(datamedida=="presion"){
					array=label_presion;
				}else if(datamedida=="diametro"){
					array=label_diametro;	
				}else if(datamedida=="distancia"){
					array=label_distancia;	
				}else{
					array=null;
					alert("ERROR: data-rel no definido");
				}	
				
				var order_array=$("input[name='"+datarel+"']").val();
				order_array++;
				if(order_array>=array.length){
					order_array=1;
				}
				$("input[name='"+datarel+"']").val(order_array);
				$(this).find("span").text(array[order_array])
				
			}else{
				
			}
			

		}
	})
	
	

	
	
	$("#primer_uso .boton").on(clickHandler,function(e){
		
		var bloque_input_puntos_q=$(".bloque_input_puntos:visible").length;
		
		console.log("--bloque_input_puntos_q:"+bloque_input_puntos_q);

		if(bloque_input_puntos_q==1){
			$("#primer_uso .boton span").addClass("none");
			$("#primer_uso .boton span:nth-child(2)").removeClass("none");
			$("#datos_Q_H .bloque_input_puntos:nth-child(4)").removeClass("none");
			
			$(".aviso_puntos p").addClass("none");
			$(".aviso_puntos p").eq(1).removeClass("none");
		}else if(bloque_input_puntos_q==2){
			var valor_caudal_maximo=$(".bloque_input_puntos:nth-child(4) input.ingreso_Q_H").eq(0).val();
			$(".aviso_puntos p").addClass("none");
			$(".aviso_puntos p").eq(2).removeClass("none");			

			console.log(valor_caudal_maximo);
			
			var valor_caudal_itermedio=0;
			if(valor_caudal_maximo>5){
				valor_caudal_itermedio=Math.round(valor_caudal_maximo/2)
			}else{
				valor_caudal_itermedio=redondear1decimal(valor_caudal_maximo/2);
			}
			
			console.log(valor_caudal_itermedio);
			
			$(".bloque_input_puntos:nth-child(5) .input_readonly").text(valor_caudal_itermedio);
			$(".bloque_input_puntos:nth-child(5) input.ingreso_Q_H").eq(0).val(valor_caudal_itermedio);
			
			$("#datos_Q_H .bloque_input_puntos:nth-child(5)").removeClass("none");
			$("#primer_uso").addClass("none");
			$("#continuar_2tab").removeClass("none");
			$("#botones_datos_Q_H").removeClass("none");
			
		}
		
		
		
		return false;
	});
	
	$("#imagen_guia").css({"width":(anchoDispositivo-20)+"px"});
	$(".img_cota, .img_perdidas").css({"width":(anchoDispositivo-20)+"px"});
		
	$(".question_box[data-rel=entradas_incompletas] .answer.yes").on(clickHandler,function(e){
		console.log("respondió si");
		var entradasQ=$("#datos_Q_H input[type='number'][name='Q[]']");
		var entradasH=$("#datos_Q_H input[type='number'][name='H[]']");
		
		$.each(entradasQ, function( index, value ) {
			console.log($(value).val());
			console.log($(entradasH[index+1]).val());
			if($(value).val()==0 || $(entradasH[index+1]).val()==0){
				//alert("XD");
				$(value).parents(".bloque_input_puntos").remove();

			}
		});
		
		revisar_precision();
		
		revisar_pase_tab3();
		
		$("#cortina").animate({
			opacity: 0
		}, 200, function() {
			$("#cortina").addClass("none");
			$(".ventanaPopup").addClass("none");
			/*console.log("--Animation complete");*/
		});
	});	
	
	
	$("input[name=cota]").on("focus",titilar_hmax);
	$("input[name=succion2]").on("focus",titilar_cotamax);
	
	$("input[name='PO_Ht[]'],input[name='Ht[]']").on("focus",titilar_perdidaH);
	$("input[name='PO_Qt[]'],input[name='Qt[]']").on("focus",titilar_perdidaQ);
	
	
	
	$("#selector_tipo_curva .opciones").on(clickHandler,function(e){
		console.log("->#selector_tipo_curva opciones");
		var data_rel=$(this).attr("data-rel");
		
		if(data_rel=="p_operacion"){
			$("input[name=tab_PO]").prop("checked",true);
			$("#imagen_guia2 .punto_operacion").removeClass("none");
			$("#imagen_guia2 .friccion").addClass("none");
			
			$("div.tab[page=3] span.help").attr("popup","punto_operacion");
			
		}else{
			$("input[name=tab_PO]").prop("checked",false);
			$("#imagen_guia2 .punto_operacion").addClass("none");
			$("#imagen_guia2 .friccion").removeClass("none");	
			$("div.tab[page=3] span.help").attr("popup","perdidas_friccion");
			
		}
		
		$("#selector_tipo_curva .opciones").removeClass("selected");
		$(this).addClass("selected");
		$(this).find("input[type='radio']").prop("checked",true);
		$(".pestana").addClass("none");
		$(".pestana."+data_rel).removeClass("none");
		
	})
	
	$(".question_box[data-rel=rpm_fuera_de_rango] .answer.yes").on(clickHandler,function(e){
		console.log("respondió si");
		swipe(2);
		$("#cortina").animate({
			opacity: 0
		}, 200, function() {
			$("#cortina").addClass("none");
			$(".ventanaPopup").addClass("none");
			/*console.log("--Animation complete");*/
		});
	});	
	
	$(".question_box[data-rel=rpm_fuera_de_rango] .answer.no").on(clickHandler,function(e){
		console.log("respondió no");
		$("#cortina").animate({
			opacity: 0
		}, 200, function() {
			$("#cortina").addClass("none");
			$(".ventanaPopup").addClass("none");
			$("input[name=rpm1]").focus();
			/*console.log("--Animation complete");*/
		});
	});		

	$(".question_box[data-rel=cota_mayor] .answer.yes").on(clickHandler,function(e){
		console.log("respondió si");
			swipe(3);
			/*
			curva_de_bomba_y_sistema();
			swipe(4);
			guardarDatos();	
			*/
		$("#cortina").animate({
			opacity: 0
		}, 200, function() {
			$("#cortina").addClass("none");
			$(".ventanaPopup").addClass("none");
		});
	});	
	
	$(".question_box[data-rel=cota_mayor] .answer.no").on(clickHandler,function(e){
		console.log("respondió no");
		$("#cortina").animate({
			opacity: 0
		}, 200, function() {
			$("#cortina").addClass("none");
			$(".ventanaPopup").addClass("none");
			$("input[name=succion2]").focus();
			/*console.log("--Animation complete");*/
		});
	});		

	$('a.boton.page5_curvas').on(clickHandler, function(e) {
		console.log("->a.boton.page5_curvas.touchstart");
		e.preventDefault();
		var cota=$('input[name="cota"]').val();
		var PO_Ht=$('input[name="PO_Ht[]"]').val();
		
		if(PO_Ht<cota){
			$('input[name="PO_Ht[]"]').val(cota);
		}
		$('input[name="PO_Ht[]"]').attr("min",cota);
		
		if(parseFloat($('#frm_curvas_de_sistema input[name="cota"]').val())>parseFloat($('#frm_curvas_de_sistema input[name="succion2"]').val())){
			swipe(5);
		}else{
			$(".question_box[data-rel=cota_mayor]").fadeInFlex();
		}
		
	});
	
	$('a.boton.page4_curvas').on(clickHandler, function(e) {
		console.log("->a.boton.page4_curvas.touchstart");
		/*		alert("clicked or tapped. This button used: " + clickHandler);*/
		
		e.preventDefault();
		
		//window.myScatter=NULL;
		
		var entradas=$("#datos_Q_H input[type='number']");
		var vacio=0;
		
		$.each(entradas, function( index, value ) {
			//console.log($(value).val());
			if($(value).val()>0){
				
			}else{
				vacio++;
			}
		});
		
		console.log("entradas vacias: "+vacio);
		
		if(vacio>0){
			$(".question_box[data-rel=entradas_incompletas]").fadeInFlex();
		}else{
			revisar_pase_tab3();
		}
	});
	
	
	
	
	$("body").on(clickHandler,'a.boton.page2_curvas:not(.off)', function(e) {
		//calcular_puntos_desde_datos();
		swipe(2);
	});

	$("body").on(clickHandler,'a.boton.page3_curvas:not(.off)', function(e) {
		calcular_puntos_desde_datos();
		//swipe(2);
	});	
	
	
	$('#frm_curvas_de_sistema a.add_Q_H').on(clickHandler, function(){
		var campos=$("<div class=\"bloque_input_puntos\"> <div class=\"espacio_boton\"> </div> <div class=\"input_puntos\"> <input type=\"number\" step=\"any\" name=\"Q[]\" required=\"\" value=\"\" class=\"ingreso_Q_H\"> </div><div class=\"input_puntos\"> <p><input type=\"number\" step=\"any\" name=\"H[]\" required=\"\" value=\"\" class=\"ingreso_Q_H\"></p> </div> <div class=\"espacio_boton\"> </div> </div>");
		$("#datos_Q_H").append(campos);
		$("#DIV_remove_Q_H").removeClass("none");
		revisar_precision();
		/*$(".input_puntos").css({"width":input_puntos_w+"px"});*/
	});
	
	$("#datos_Q_H").on("blur",".input_puntos input",function(){
		//alert("XD");
		generarPrevista();
	});
		
	$('#frm_curvas_de_sistema a.remove_Q_H').on(clickHandler, function(){
		
		if($("#datos_Q_H .bloque_input_puntos").length>=3){
			$("#datos_Q_H .bloque_input_puntos:last-child").remove();
			if($("#datos_Q_H .bloque_input_puntos").length==3){
				$("#DIV_remove_Q_H").addClass("none");
				
			}
		}else{
			$("#DIV_remove_Q_H").addClass("none");
			
			
		}
		
		revisar_precision();
		return false;
	});	
	
	$('#frm_curvas_de_sistema a.add_Q_H_tuberias').on(clickHandler, function(){
		var campos=$("<div class=\"bloque\"><p><input type=\"number\" step=\"any\" name=\"Q[]\" value=\"\" class=\"tuberias\" placeholder=\"0\"></p></div><div class=\"bloque\"><p><input type=\"number\" step=\"any\" name=\"H[]\" value=\"\" class=\"tuberias\" placeholder=\"0\"></p></div>");
		$("#datos_Q_H_tuberias").append(campos);
		$("#DIV_remove_Q_H_tuberias").removeClass("none");
	});	
	
	$('#frm_curvas_de_sistema a.remove_Q_H_tuberias').on(clickHandler, function(){
		
		if($("#datos_Q_H_tuberias .bloque").length>=4){
			$("#datos_Q_H_tuberias .bloque:last-child").remove();
			$("#datos_Q_H_tuberias .bloque:last-child").remove();
			if($("#datos_Q_H_tuberias .bloque").length==4){
				$("#DIV_remove_Q_H_tuberias").addClass("none");
			}
		}else{
			$("#DIV_remove_Q_H_tuberias").removeClass("none");
		}
		
		if($("#datos_Q_H_tuberias .bloque").length>=8){
			if($("#datos_Q_H_tuberias .bloque").length==8){
				$("#DIV_add_Q_H_tuberias").addClass("none");
			}
		}else{
			$("#DIV_add_Q_H_tuberias").removeClass("none");
		}		
		

	});		
	
	$("span.help[popup]").on(clickHandler,function(){
		var div_popup=$(this).attr("popup");
		$("#"+div_popup).fadeInFlex();
	});
	
	//$('#frm_curvas_de_sistema').on('submit', function(e) {
	$('a.boton.page6_curvas').on(clickHandler, function(e) {
		console.log("->#frm_curvas_de_sistema submit");
		e.preventDefault();
		
		$('#frm_curvas_de_sistema input[name="frecuencia2"]').val($('#frm_curvas_de_sistema input[name="frecuencia1"]').val());

		graficarFlag=1;
		$("select[name='exponente'] option:disabled").prop("disabled",false);		
		$("select[name='exponente'] option[value=4]").prop("selected",true);		

		curva_de_bomba_y_sistema();
		swipe(6);
	});	
	
	$('#frm_curvas_de_sistema input[name="cota"], #frm_curvas_de_sistema input[name="succion2"]').on('change', function(){
		actualizarNivelAguaSuccion();
	});
	
	$('#frm_curvas_de_sistema').on(clickHandler,'.boton.nivel_agua:not(.off)', function(e){
		flagNFF=1;
		console.log("-> .boton.nivel_agua");
		console.log("--datosCurvaSistema2");
		console.log(datosCurvaSistema2);
		
		var nivelActual=parseFloat($('#frm_curvas_de_sistema input[name="succion1"]').val());
		var paso=$('#frm_curvas_de_sistema input[name="succion1"]').attr('max')/10;
		
		var q_digitos_nivelActual=Math.floor(nivelActual).toString().length;
		console.log(q_digitos_nivelActual);		
		
		var exponente = $("select[name='exponente'] option:selected").val()
		
		console.log("nivelActual: "+nivelActual);
		
		if($(this).hasClass("subir")){
			console.log("subir");
			
			
			/*
			if(q_digitos_nivelActual>1){
				nivelNew=nivelActual+(10*(q_digitos_nivelActual-1));						
			}else{
				nivelNew=nivelActual+1;				
			}
			*/
			
			nivelNew=nivelActual+paso;		
			
			console.log("nivelNew: "+nivelNew);
			
			if(nivelNew>=$('#frm_curvas_de_sistema input[name="succion1"]').attr('max')){
				$(this).addClass("off");
				nivelNew=$('#frm_curvas_de_sistema input[name="succion1"]').attr('max');
			}else{
				$('#frm_curvas_de_sistema .boton.nivel_agua.bajar').removeClass("off");
				
			}
		}else{
			console.log("bajar");
			/*
			if(q_digitos_nivelActual>1){
				nivelNew=nivelActual-(10*(q_digitos_nivelActual-1));						
			}else{
				nivelNew=nivelActual-1;				
			}
			*/
			nivelNew=nivelActual-paso;	
			
			console.log("nivelNew: "+nivelNew);
			if(nivelNew<=parseFloat($('#frm_curvas_de_sistema input[name="succion1"]').attr('min'))){
				$(this).addClass("off");
				nivelNew=$('#frm_curvas_de_sistema input[name="succion1"]').attr('min');
			}else{
				$('#frm_curvas_de_sistema .boton.nivel_agua.subir').removeClass("off");	
			}			
		}
		
		//alert(nivelNew);
		
		$('#frm_curvas_de_sistema input[name="succion1"]').val(redondear2decimal(nivelNew));	
		
		
		if($("input[name=radio_tipo_curva]:checked").val()=="p_operacion"){
			datosarr=PuntosQH2Object("#frm_curvas_de_sistema input[name='PO_Qt[]'].tuberias","#frm_curvas_de_sistema  input[name='PO_Ht[]'].tuberias");
		}else{
			datosarr=PuntosQH2Object("#frm_curvas_de_sistema input[name='Qt[]'].tuberias","#frm_curvas_de_sistema  input[name='Ht[]'].tuberias");
		}
		
		cota=parseFloat($("#frm_curvas_de_sistema input[name='cota']").val())-parseFloat($("#frm_curvas_de_sistema input[name='succion1']").val());
		var frecuencia1 = $("#frm_curvas_de_sistema input[name='frecuencia1']").val();
		var frecuencia2 = $("#frm_curvas_de_sistema input[name='frecuencia2']").val();
	
		var Qmax =limitesObjeto.limites_graf.x.max;
		
		if($("input[name=radio_tipo_curva]:checked").val()=="p_operacion"){
			datosCurvaSistema=jccdS(datosarr,cota,parseFloat($("#frm_curvas_de_sistema input[name='cota']").val()),Qmax,frecuencia1,frecuencia2);
		}else{
			datosCurvaSistema=jccdS(datosarr,cota,Qmax,null,frecuencia1,frecuencia2);
		}	
	
		curva_de_sistema(datosarr,datosCurvaSistema,2);
		scatterData[3]=datosCurvaSistema;
		scatterData[6]=interseccion_curva_bomba_sistema(datosCurvaSistema,scatterData[1],exponente);
		label_interseccion_curva_bomba_sistema(scatterData[6]);
		
		var ctx = document.getElementById('canvas').getContext('2d');
		//var limitesObjeto=null;
		//var scatterData=null;
		generarGrafico(ctx,scatterChartData,configuracionGrafico,limitesObjeto,scatterData);
		
	});	
/*
	$('select[name="exponente"]').on('change', function(){
		if(typeof(datosCurvaBomba.nB)=="undefined"){
			
		}else{
			curva_de_bomba_frec();
		}
	});
*/
	$('select[name="exponente"]').on('change', function(){
		$('#frm_curvas_de_sistema input[name="frecuencia2"]').val($('#frm_curvas_de_sistema input[name="frecuencia1"]').val());
		var exponente = $("select[name='exponente'] option:selected").val();
		actualizar_curva_de_bomba();
		cerrarPopup();
		

	});	
	

	
	
	$('#frm_curvas_de_sistema input[name="succion1"]').on('change', function(){
		//alert("XD");
		flagNFF=1;
		
		console.log("--datosCurvaSistema2");
		console.log(datosCurvaSistema2);
		var exponente = $("select[name='exponente'] option:selected").val()
		
		
		console.log(parseFloat($('#frm_curvas_de_sistema input[name="succion1"]').val()));
		console.log(parseFloat($('#frm_curvas_de_sistema input[name="succion1"]').attr('max')));
		
		if(parseFloat($('#frm_curvas_de_sistema input[name="succion1"]').val())>=parseFloat($('#frm_curvas_de_sistema input[name="succion1"]').attr('max'))){
			$('#frm_curvas_de_sistema .boton.nivel_agua.subir').addClass("off");
			
			$("#alert_box h1").text("Fuera de rango");
			$("#alert_box p.msg").text("La medida ingresada supera el máximo permitido");
			$("#alert_box").fadeInFlex();
			$('#frm_curvas_de_sistema input[name="succion1"]').val($('#frm_curvas_de_sistema input[name="succion1"]').attr('max'));
		}else{
			$('#frm_curvas_de_sistema .boton.nivel_agua.subir').removeClass("off");
		}
		
		if(parseFloat($('#frm_curvas_de_sistema input[name="succion1"]').val())<parseFloat($('#frm_curvas_de_sistema input[name="succion1"]').attr('min'))){
			$('#frm_curvas_de_sistema .boton.nivel_agua.bajar').addClass("off");
			$("#alert_box h1").text("Fuera de rango");
			$("#alert_box p.msg").text("La medida ingresada supera el mínimo permitido");
			$("#alert_box").fadeInFlex();
			$('#frm_curvas_de_sistema input[name="succion1"]').val($('#frm_curvas_de_sistema input[name="succion1"]').attr('min'));			
			
		}else{
			$('#frm_curvas_de_sistema .boton.nivel_agua.bajar').removeClass("off");
		}
		
		
		if($("input[name=radio_tipo_curva]:checked").val()=="p_operacion"){
			datosarr=PuntosQH2Object("#frm_curvas_de_sistema input[name='PO_Qt[]'].tuberias","#frm_curvas_de_sistema  input[name='PO_Ht[]'].tuberias");
		}else{
			datosarr=PuntosQH2Object("#frm_curvas_de_sistema input[name='Qt[]'].tuberias","#frm_curvas_de_sistema  input[name='Ht[]'].tuberias");
		}
		
		cota=parseFloat($("#frm_curvas_de_sistema input[name='cota']").val())-parseFloat($("#frm_curvas_de_sistema input[name='succion1']").val());
		var frecuencia1 = $("#frm_curvas_de_sistema input[name='frecuencia1']").val();
		var frecuencia2 = $("#frm_curvas_de_sistema input[name='frecuencia2']").val();
		
		var Qmax =limitesObjeto.limites_graf.x.max;
		
		if($("input[name=radio_tipo_curva]:checked").val()=="p_operacion"){
			datosCurvaSistema=jccdS(datosarr,cota,parseFloat($("#frm_curvas_de_sistema input[name='cota']").val()),Qmax,frecuencia1,frecuencia2);
		}else{
			datosCurvaSistema=jccdS(datosarr,cota,null,Qmax,frecuencia1,frecuencia2);
		}	
		
		//curva_de_sistema(datosarr, datosCurvaSistema, 2);
		//scatterData[6]=interseccion_curva_bomba_sistema(datosCurvaSistema2,datosCurvaBombaActualizable,exponente);	
		scatterData[6]=interseccion_curva_bomba_sistema(datosCurvaSistema,scatterData[1],exponente);
		label_interseccion_curva_bomba_sistema(scatterData[6]);		

		var ctx = document.getElementById('canvas').getContext('2d');
		//var limitesObjeto=null;
		//var scatterData=null;		
		generarGrafico(ctx,scatterChartData,configuracionGrafico,limitesObjeto,scatterData);
	});	
		
	$('#frm_curvas_de_sistema').on(clickHandler,'.boton.frecuencia:not(.off)', function(){
		
		var otra_frecuencia=parseFloat($('#frm_curvas_de_sistema input[name="frecuencia2"]').val());
		if($(this).hasClass("subir")){
			frecNew=otra_frecuencia+1;
			if(frecNew>=$('#frm_curvas_de_sistema input[name="frecuencia1"]').val()){
				$(this).addClass("off");
				frecNew=$('#frm_curvas_de_sistema input[name="frecuencia1"]').val();
			}else{
				$('#frm_curvas_de_sistema .boton.frecuencia.bajar').removeClass("off");
				
			}

		}else{
			frecNew=otra_frecuencia-1;
			if(frecNew<$('#frm_curvas_de_sistema input[name="frecuencia2"]').attr("min")){
				$(this).addClass("off");
				frecNew=$('#frm_curvas_de_sistema input[name="frecuencia2"]').attr("min");
			}else{
				$('#frm_curvas_de_sistema .boton.frecuencia.subir').removeClass("off");	
			}			
		}
		$('#frm_curvas_de_sistema input[name="frecuencia2"]').val(frecNew);				
		curva_de_bomba_frec(1);
	});	
		
	$("#frm_curvas_de_sistema input[name='frecuencia1']").on("change",function(){
		var frec=$("#frm_curvas_de_sistema input[name='frecuencia1']").val();
		$("#frm_curvas_de_sistema input[name='frecuencia2']").val(frec).attr("max",frec);
	});
	
	$("#frm_curvas_de_sistema input[name='frecuencia2']").on("change",function(){
		
		
		
		if(parseFloat($('#frm_curvas_de_sistema input[name="frecuencia2"]').val())>=parseFloat($('#frm_curvas_de_sistema input[name="frecuencia2"]').attr('max'))){
			$('#frm_curvas_de_sistema .boton.frecuencia.subir').addClass("off");
			$("#alert_box h1").text("Fuera de rango");
			$("#alert_box p.msg").text("La frecuencia ingresada supera el máximo permitido");
			$("#alert_box").fadeInFlex();
			$('#frm_curvas_de_sistema input[name="frecuencia2"]').val($('#frm_curvas_de_sistema input[name="frecuencia2"]').attr('max'));
		}else{
			$('#frm_curvas_de_sistema .boton.frecuencia.subir').removeClass("off");
		}
		
		if(parseFloat($('#frm_curvas_de_sistema input[name="frecuencia2"]').val())<=parseFloat($('#frm_curvas_de_sistema input[name="frecuencia2"]').attr('min'))){
			$('#frm_curvas_de_sistema .boton.frecuencia.bajar').addClass("off");
			$("#alert_box h1").text("Fuera de rango");
			$("#alert_box p.msg").text("La frecuencia ingresada supera el mínimo permitido");
			$("#alert_box").fadeInFlex();
			$('#frm_curvas_de_sistema input[name="frecuencia2"]').val($('#frm_curvas_de_sistema input[name="frecuencia2"]').attr('min'));
		}else{
			$('#frm_curvas_de_sistema .boton.frecuencia.bajar').removeClass("off");
		}
		
		curva_de_bomba_frec();
		//jccd(1);
	});
	
	$("#frm_curvas_de_sistema select[name='unidadesCaudal'], #frm_curvas_de_sistema select[name='unidadesAltura'] ").on("change",function(){
		actualizarUnidMedidas();
	});	
	
	$("#frm_curvas_de_sistema select[name='sfrecuencia1']").on("change",function(){
		$("#frm_curvas_de_sistema input[name='frecuencia1']").val($("#frm_curvas_de_sistema select[name='sfrecuencia1']").val());
	});	
		
	/*curvas de bomba y de sistema*/
}

function calcular_puntos_desde_datos(){
	console.log("->calcular_puntos_desde_datos");
		
	puntos_calculados=[];
	
	var pap_datosfijos=null;/*puntos_a_procesar_datosfijos*/
	var input_datas=$("#form_puntos_a_procesar_datos_fijos input");
	const obj = {};
	
	var flag_error_input=false;
	$.each( input_datas, function( key, input_data ) {
		console.log($(input_data).attr("name"));
		console.log($(input_data).val());
		
		
		if($(input_data).prop("required")==true && $(input_data).val()=="" && flag_error_input==false){
			flag_error_input=true;
		}
		
		if(flag_error_input==true){
			

			
			return false;
			//console.log("break ;)");
		}else{
			obj[$(input_data).attr("name")]=$(input_data).val();
			//$(input_data).val("");			
		}

	});

	if(flag_error_input==true){
		console.log("break ;)");
		$("#alert_box h1").text("Datos incompletos");
		$("#alert_box p.msg").text("No ha llenado todos los campos necesarios");
		$("#alert_box").fadeInFlex();
	}else{
		//puntos_a_procesar_datosfijos.push(obj);	
		pap_datosfijos=obj;	
	}
	
	console.log("--puntos_a_procesar_datosfijos");
	console.log(pap_datosfijos);
	
	

	//if(puntos_a_procesar.length>=3){
		
		
		/*
		var puntos_a_procesar=[
		{D1: "200", D2: "125", Deq: "", Kf: "", P1: "-1.02", P2: "32.64", Q: "71", Z: "1.2", d_D1: "1", d_D2: "1", d_Deq: "1", d_P1: "1", d_P2: "1", d_Q: "1", d_Z: "1", d_hf: "1", hf: "0.2", rpm: "3500" },
		{ D1: "200", D2: "125", Deq: "", Kf: "", P1: "-3.06", P2: "26.52", Q: "113", Z: "1.2", d_D1: "1", d_D2: "1", d_Deq: "1", d_P1: "1", d_P2: "1", d_Q: "1", d_Z: "1", d_hf: "1", hf: "1.2", rpm: "3500" },
		{D1: "200",D2: "125",Deq: "", Kf: "", P1: "-5.61", P2: "16.32", Q: "142", Z: "1.2", d_D1: "1", d_D2: "1", d_Deq: "1" , d_P1: "1", d_P2: "1", d_Q: "1", d_Z: "1", d_hf: "1", hf: "0.4", rpm: "3500"}
		];*/
		
		console.log(puntos_a_procesar);
		
		
		$.each(puntos_a_procesar, function(index, punto){
			console.log(punto);
			console.log(punto.D1);			
			
			puntos_calculados.push(calcular_punto_caudal_altura(
				punto.Q,
				punto.d_Q	,
				pap_datosfijos.D1,
				pap_datosfijos.d_D1,
				punto.P1,
				punto.d_P1,
				punto.Z,
				punto.d_Z,
				punto.hf,
				punto.d_hf,
				punto.hf =="" ? 0 : 1,
				pap_datosfijos.D2,
				pap_datosfijos.d_D2,
				punto.P2,
				punto.d_P2,
				punto.rpm,
				null,
				pap_datosfijos.Kf =="" ? 0 : 1,
				pap_datosfijos.Kf,
				pap_datosfijos.Deq,
				pap_datosfijos.d_Deq
			));
			
		});
		console.log("--puntos_calculados");
		
		/*
		puntos_calculados=[
		{ Q: 71, H: 35.17155409381498, hf: 0.2 },
		{ Q: 113, H: 31.36256977264896, hf: 0.3 },
		{ Q: 143, H: 23.982523242297642, hf: 0.4 }];
		*/
		console.log(puntos_calculados);
		
		//alert("pause");
		
		swipe(3);
		
	/*}else{
		$("#alert_box h1").text("Puntos incompletos");
		$("#alert_box p.msg").text("Necesita al menos 3 puntos para continuar");
		$("#alert_box").fadeInFlex();
	}*/
		
}

function borrar_punto(){
	console.log("->borrar_punto");
	console.log("--puntero_entrada: "+puntero_entrada);
	console.log("--puntos_a_procesar.length: "+puntos_a_procesar.length);
	console.log("--puntos_a_procesar: ");
	console.log(puntos_a_procesar);
	puntos_a_procesar.splice(puntero_entrada,1);
	
	console.log("--puntos_a_procesar: ");
	console.log(puntos_a_procesar);	
	
	var ElemContenedor=$("#form_puntos_a_procesar");
	var ElemAMover=$("#form_puntos_a_procesar>.wrapper");
	refrescarPuntoEntrada();
	
	console.log(JSON.stringify(puntos_a_procesar[puntero_entrada]));
	
	if(typeof(puntos_a_procesar[puntero_entrada])=="undefined"){
		animarSlide(ElemContenedor,ElemAMover,"toBottom","",null);
	}else{
		animarSlide(ElemContenedor,ElemAMover,"toBottom","",JSON.stringify(puntos_a_procesar[puntero_entrada]));
	}
	
	
	
}

function arrow_prev(){
	console.log("->arrow_prev");
	//alert("XD");
			
	var ElemContenedor=$("#form_puntos_a_procesar");
	var ElemAMover=$("#form_puntos_a_procesar>.wrapper");
	puntero_entrada--;
	refrescarPuntoEntrada();
	
	console.log(JSON.stringify(puntos_a_procesar[puntero_entrada]));
	
	animarSlide(ElemContenedor,ElemAMover,"toRight","",JSON.stringify(puntos_a_procesar[puntero_entrada]));
	
	
	
}

function arrow_next(){
	console.log("->arrow_next");
	//alert("XD");
	
	console.log("--puntero_entrada: "+puntero_entrada);
	console.log("--puntos_a_procesar.length: "+puntos_a_procesar.length);
	
	var ElemContenedor=$("#form_puntos_a_procesar");
	var ElemAMover=$("#form_puntos_a_procesar>.wrapper");	

	console.log(JSON.stringify(puntos_a_procesar[puntero_entrada]));
	
	if(puntero_entrada>=puntos_a_procesar.length){
		console.log("-->aumentar");
		var input_datas=$("#form_puntos_a_procesar input");
		const obj = {};
		
		var flag_error_input=false;
		$.each( input_datas, function( key, input_data ) {
			console.log($(input_data).attr("name"));
			console.log($(input_data).val());
			
			
			if($(input_data).prop("required")==true && $(input_data).val()=="" && flag_error_input==false){
				flag_error_input=true;
			}
			
			if(flag_error_input==true){
				

				
				return false;
				//console.log("break ;)");
			}else{
				obj[$(input_data).attr("name")]=$(input_data).val();
				//$(input_data).val("");			
			}

		});

		if(flag_error_input==true){
			console.log("break ;)");
			$("#alert_box h1").text("Datos incompletos");
			$("#alert_box p.msg").text("No ha llenado todos los campos necesarios");
			$("#alert_box").fadeInFlex();
		}else{
			puntos_a_procesar.push(obj);
			animarSlide(ElemContenedor,ElemAMover,"toLeft",".clean",null);
			puntero_entrada++;
					
		}	
		
		console.log(puntos_a_procesar);
		//return false;	
	}
	else{
		console.log("-->mover");
		puntero_entrada++;
		console.log("--puntero_entrada: "+puntero_entrada);
		console.log(JSON.stringify(puntos_a_procesar[puntero_entrada]));
		var JSON_puntos_a_procesar=null;
		if(typeof(puntos_a_procesar[puntero_entrada])!="undefined"){
			JSON_puntos_a_procesar=JSON.stringify(puntos_a_procesar[puntero_entrada]);
		}
		animarSlide(ElemContenedor,ElemAMover,"toLeft",".clean",JSON_puntos_a_procesar);	
		
	}
	console.log("--puntero_entrada: "+puntero_entrada);
	refrescarPuntoEntrada();
}

function refrescarPuntoEntrada(){
	console.log("->refrescarPuntoEntrada");
	console.log("--puntero_entrada: "+puntero_entrada);
	console.log("--puntos_a_procesar.length: "+puntos_a_procesar.length);
	
	$("#puntero_entrada_num").text((puntero_entrada+1));
	if(puntero_entrada>0){
		$("#arrow_prev").removeClass("off");
	}else{
		$("#arrow_prev").addClass("off");
	}
	
	if(puntero_entrada<puntos_a_procesar.length){
		$("#arrow_next").removeClass("add");
	}else{
		$("#arrow_next").addClass("add");
	}	
	
	if(puntos_a_procesar.length>0 && puntero_entrada<puntos_a_procesar.length){
		$("#borrar_punto").removeClass("off");
	}else{
		$("#borrar_punto").addClass("off");
	}
	
	if(puntos_a_procesar.length>=1){
		$("a.boton.page2_curvas").removeClass("off");
	}else{
		$("a.boton.page2_curvas").addClass("off");
	}
	
	
	
}

function actualizarNivelAguaSuccion(){
	console.log("->actualizarNivelAguaSuccion");
	var hk_curva1=parseFloat($('#frm_curvas_de_sistema input[name="cota"]').val());
	$('#frm_curvas_de_sistema p.input_readonly.curva1_hk').text(hk_curva1);
	var cota_curva2=parseFloat($('#frm_curvas_de_sistema input[name="succion1"]').val());
	var cota_curva3=parseFloat($('#frm_curvas_de_sistema input[name="succion2"]').val());
	
	$('#frm_curvas_de_sistema p.input_readonly.curva2_hk').text(hk_curva1-cota_curva2);
	$('#frm_curvas_de_sistema p.input_readonly.curva3_hk').text(redondear2decimal(hk_curva1-cota_curva3));
	$('#frm_curvas_de_sistema input[name="succion1"]').val("0");
	$('#frm_curvas_de_sistema input[name="succion1"]').attr("max",	$('#frm_curvas_de_sistema input[name="succion2"]').val());

}

function actualizarUnidMedidas(){
	console.log("->actualizarUnidMedidas");
	//unidadMedida=datosUnidadMedida[$("#frm_curvas_de_sistema select[name='unidades']").val()];
	
	$("#frm_curvas_de_sistema span.unidMedida.Q").text($("#frm_curvas_de_sistema select[name='unidadesCaudal']").val());
	$("#frm_curvas_de_sistema span.unidMedida.H").text($("#frm_curvas_de_sistema select[name='unidadesAltura']").val());
	//$(".select_unidades" ).addClass("none")	
}

function revisar_precision(){
	console.log("->revisar_precision");
	console.log("DEPRECATED");
	/*
	console.log($("#datos_Q_H .bloque_input_puntos").length);
	if($("#datos_Q_H .bloque_input_puntos").length==3){
		$("#DIV_remove_Q_H").addClass("none");
		$(".boton.add_Q_H").removeClass("none");
		$(".grafico_dots .dot:nth-child(4)").addClass("none");
		$(".grafico_dots .dot:nth-child(5)").addClass("none");
		$(".grafico_dots .dot").addClass("q3");	
		$(".grafico_dots .dot").removeClass("q4");	
	}else if($("#datos_Q_H .bloque_input_puntos").length==4){	
		$(".nivel_precision").removeClass("none");
		$(".boton.add_Q_H").removeClass("none");
		$(".grafico_dots .dot:nth-child(4)").removeClass("none");
		$(".grafico_dots .dot:nth-child(5)").addClass("none");		
		$(".grafico_dots .dot").removeClass("q3");	
		$(".grafico_dots .dot").addClass("q4");	
	}else if($("#datos_Q_H .bloque_input_puntos").length>4){
		$(".nivel_precision").removeClass("none");
		$(".boton.add_Q_H").addClass("none");
		$(".grafico_dots .dot:nth-child(4)").removeClass("none");
		$(".grafico_dots .dot:nth-child(5)").removeClass("none");
		$(".grafico_dots .dot").removeClass("q3");	
		$(".grafico_dots .dot").removeClass("q4");			
	}
	$(".aviso_puntos span").text(($("#datos_Q_H .bloque_input_puntos").length));
	*/
}

function hallar_RPM(){
	var frecuencia1=$('#frm_curvas_de_sistema [name="frecuencia1"]').val();
	var frecuencia2=$('#frm_curvas_de_sistema [name="frecuencia2"]').val();
	rpm_n=$('#frm_curvas_de_sistema [name="rpm1"]').val();
	
	$('#rpm2').text(Math.round(frecuencia2*(rpm_n/frecuencia1)));
	$('#porcentaje').text(Math.round(frecuencia2*(100/frecuencia1)));
}

var limites_graf={
		x:{min:0,max:0},
		y:{min:0,max:0}
	}
	
var limites_visuales_graf={
		x:{min:0,max:0},
		y:{min:0,max:0}
	}
	
var datosPuntos=[];
var datosInterseccion=[{x:0,y:0}];
var datosCurvaBomba=[];
var datosPrevista=[];
var datosCurvaBombaActualizable=[];
var datosCurvaSistema1=[];
var datosCurvaSistema2=[];
var datosCurvaSistema3=[];
var graficarFlag=0;//bandera de que se ha presionado graficar

var datosUnidadMedida=[
	{Q:"l/s", h:"m"},
	{Q:"l/min",  h:"m"},
	{Q:"m³/h",  h:"m"},
	{Q:"GPM",  h:"m"},
	{Q:"GPM",  h:"pies"}
];


var curva_bomba_Lcoord;
var curva_sistema_Lcoord;
var curva_bomba_nB;
var curva_bombaActualisable_nB;
var curva_sistema_nB;

function actualizar_curva_de_bomba(){
	var datosarr=PuntosQH2Object("#frm_curvas_de_sistema  input[name='Q[]'].ingreso_Q_H","#frm_curvas_de_sistema  input[name='H[]'].ingreso_Q_H");
	
	var exponente=$("select[name='exponente'] option:selected").val(); 
	console.log("exponente : "+exponente);
	
	var curva_de_bomba_f=curva_de_bomba(datosarr,exponente);

	curva_de_bomba_f.then(
		function(result_curva_de_bomba){
			console.log(result_curva_de_bomba);
			
			datosCurvaBomba=result_curva_de_bomba;
			datosCurvaBombaActualizable=result_curva_de_bomba;
			
			scatterData[0]=result_curva_de_bomba;//datosCurvaBomba
			scatterData[1]=result_curva_de_bomba;//datosCurvaBombaActualizable
			
			$(".output_data .spanHz").text($("input[name='frecuencia1']").val());
			
			var promedio_cota=0;
			$("#frm_curvas_de_sistema input[name='succion1']").attr("max",$("#frm_curvas_de_sistema input[name='succion2']").val());
			$("#frm_curvas_de_sistema input[name='succion1']").val(promedio_cota);
			
			$('#frm_curvas_de_sistema .boton.nivel_agua').removeClass("off");
			//scatterData[6]=interseccion_curva_bomba_sistema(datosCurvaSistema2,result_curva_de_bomba,exponente);
			
			scatterData[6]=interseccion_curva_bomba_sistema(scatterData[3],result_curva_de_bomba,exponente);	
			label_interseccion_curva_bomba_sistema(scatterData[6]);			

			hallar_RPM();
			
			var ctx = document.getElementById('canvas').getContext('2d');
			//var limitesObjeto=null;
			//var scatterData=null;
			generarGrafico(ctx,scatterChartData,configuracionGrafico,limitesObjeto,scatterData);
		},
		function(reason){
			 console.log(reason); // Error!
		});
}

function label_interseccion_curva_bomba_sistema(objeto){
	console.log("->label_interseccion_curva_bomba_sistema");
	console.log(objeto);


	var div_PO=$("#div_PO");
	if(objeto.coord!=null){
		console.log(objeto.coord[0].x);
		console.log(objeto.coord[0].y);	

		if(objeto.coord[0].x>0 && objeto.coord[0].y>0){
			div_PO.removeClass("none");
			div_PO.find(".PO_Q").text((objeto.coord[0].x).toFixed(2));
			div_PO.find(".PO_h").text((objeto.coord[0].y).toFixed(2));			
		}else{
			div_PO.addClass("none");
		}
		
		

	}else{
		div_PO.addClass("none");
	}
}

var bucle_torre_verificacion_curva=0;

function torre_verificacion_curva(Qmax,exponente){	
	console.log("->torre_verificacion_curva");
	
	bucle_torre_verificacion_curva++;
	
	var datosarr=PuntosQH2Object("#frm_curvas_de_sistema  input[name='Q[]'].ingreso_Q_H","#frm_curvas_de_sistema  input[name='H[]'].ingreso_Q_H");
	var frecuencia1 = $("#frm_curvas_de_sistema input[name='frecuencia1']").val();
	var frecuencia2 = $("#frm_curvas_de_sistema input[name='frecuencia2']").val();
	var verificacion_de_curva_f=verificacion_de_curva(datosarr,frecuencia1,frecuencia2,Qmax,exponente);
		
	verificacion_de_curva_f.then(function(result_nRev){
		console.log("--result_nRev");
		console.log(result_nRev);
		//alert(result_nRev);
		if(result_nRev==0){
			if(exponente>2){
				console.log("bajamos el exponente: "+(exponente-1));
				torre_verificacion_curva(Qmax,(exponente-1));
			}else{
				//alert("Revisar los puntos ingresados");
				$("#alert_box").attr("data-rel","verificacion_de_curva");
				$("#alert_box h1").text("Algo anda mal");
				$("#alert_box p.msg").text("Revisar los puntos ingresados, alguno de ellos no corresponden a la curva de la bomba.");
				$("#alert_box").fadeInFlex();
			}
		}else{
			console.log("cambiar a exponente: "+exponente);
			console.log("bucle_torre_verificacion_curva: "+bucle_torre_verificacion_curva);
			
			
			if(bucle_torre_verificacion_curva>1){
				/*
				$("#alert_box h1").text("Cambio por necesidad");
				$("#alert_box p.msg").text("Se ha reducido a cuadrática");
				$("#alert_box").fadeInFlex();	
				*/
				bucle_torre_verificacion_curva=0;
			}
			
			preparar_select_precision_de_curva(exponente);

			$("select[name='exponente']").val(exponente);
			actualizar_curva_de_bomba();
		}
	});	
}

function preparar_select_precision_de_curva(exponente){
	console.log("->preparar_select_precision_de_curva");
	console.log("--exponente: "+exponente);
	
	if(exponente>2){
		$("#ajustes_boton").css({"right":"-100px"}).delay(500).animate({"right":"-20px"},500);
		$("#ajustes_boton").removeClass("none");
		var opciones=$("select[name='exponente'] option");
		$.each( opciones, function( key, opcion ) {
			console.log($(opcion).attr("value"));
			if(parseInt($(opcion).attr("value"))>exponente){
				$(opcion).prop("disabled",true);
			}
		});
	}else{
		$("#ajustes_boton").addClass("none");
	}
}

function curva_de_bomba_y_sistema(){
	console.log("->curva_de_bomba_y_sistema");
	
	var datosarr=PuntosQH2Object("#frm_curvas_de_sistema  input[name='Q[]'].ingreso_Q_H","#frm_curvas_de_sistema  input[name='H[]'].ingreso_Q_H");
	var exponente=$("select[name='exponente'] option:selected").val(); 

	var curva_de_bomba_f=curva_de_bomba(datosarr,exponente);
	
	curva_de_bomba_f.then(
		function(result_curva_de_bomba){
			console.log(result_curva_de_bomba);
			datosCurvaBomba=result_curva_de_bomba;
			datosCurvaBombaActualizable=result_curva_de_bomba;
			
			
			
			console.log("--scatterData");
			console.log(scatterData);
			console.log("--puntos_calculados");
			console.log(puntos_calculados);
			
			scatterData[0]=result_curva_de_bomba;//datosCurvaBomba
			scatterData[1]=result_curva_de_bomba;//datosCurvaBombaActualizable
			scatterData[5]={coord:Arr2Coords(datosarr)};
			scatterData[7]={coord:Arr2Coords(puntos_calculados)};
			
			
			var datosPuntos=PuntosQH2Object("#frm_curvas_de_sistema  input[name='Q[]'].ingreso_Q_H","#frm_curvas_de_sistema  input[name='H[]'].ingreso_Q_H");
			override={
				x:{min:0},
				y:{min:0}
			}

			//limitesObjeto=limites_grafico(result_curva_de_bomba.coord,datosPuntos,override);
			limitesObjeto=limitesbordes_grafico(result_curva_de_bomba.coord,override,limitesObjeto);
			
			var exponente = $("select[name='exponente'] option:selected").val();
			//var exponente=4;
			
			torre_verificacion_curva(limites_graf.x.max,exponente);

			
			$(".output_data .spanHz").text($("input[name='frecuencia1']").val());

			//var promedio_cota=parseFloat($("#frm_curvas_de_sistema input[name='succion2']").val())/2;
			
			var promedio_cota=0;
			$("#frm_curvas_de_sistema input[name='succion1']").attr("max",$("#frm_curvas_de_sistema input[name='succion2']").val());
			$("#frm_curvas_de_sistema input[name='succion1']").val(promedio_cota);
			
			
			if($("input[name=radio_tipo_curva]:checked").val()=="p_operacion"){
				datosarr=PuntosQH2Object("#frm_curvas_de_sistema input[name='PO_Qt[]'].tuberias","#frm_curvas_de_sistema  input[name='PO_Ht[]'].tuberias");
			}else{
				datosarr=PuntosQH2Object("#frm_curvas_de_sistema input[name='Qt[]'].tuberias","#frm_curvas_de_sistema  input[name='Ht[]'].tuberias");
			}
			
			var cota=parseFloat($("#frm_curvas_de_sistema input[name='cota']").val());
			var frecuencia1 = $("#frm_curvas_de_sistema input[name='frecuencia1']").val();
			var frecuencia2 = $("#frm_curvas_de_sistema input[name='frecuencia2']").val();
			var Qmax =limitesObjeto.limites_graf.x.max;
			if($("input[name=radio_tipo_curva]:checked").val()=="p_operacion"){
				datosCurvaSistema=jccdS(datosarr,cota,parseFloat($("#frm_curvas_de_sistema input[name='cota']").val()),Qmax,frecuencia1,frecuencia2);
			}else{
				datosCurvaSistema=jccdS(datosarr,cota,null,Qmax,frecuencia1,frecuencia2);
			}		
			
			scatterData[2]=datosCurvaSistema;
			
			curva_de_sistema(datosarr, datosCurvaSistema,1);
			console.log("--datosCurvaSistema1");
			console.log(datosCurvaSistema1);
			
			
			cota=parseFloat($("#frm_curvas_de_sistema input[name='cota']").val())-parseFloat($("#frm_curvas_de_sistema input[name='succion1']").val());
			var frecuencia1 = $("#frm_curvas_de_sistema input[name='frecuencia1']").val();
			var frecuencia2 = $("#frm_curvas_de_sistema input[name='frecuencia2']").val();
			var Qmax =limitesObjeto.limites_graf.x.max;
			if($("input[name=radio_tipo_curva]:checked").val()=="p_operacion"){
				datosCurvaSistema=jccdS(datosarr,cota,parseFloat($("#frm_curvas_de_sistema input[name='cota']").val()),Qmax,frecuencia1,frecuencia2);
			}else{
				datosCurvaSistema=jccdS(datosarr,cota,null,Qmax,frecuencia1,frecuencia2);
			}
			
			scatterData[3]=datosCurvaSistema;
			
			
			curva_de_sistema(datosarr, datosCurvaSistema,2);
			console.log("--datosCurvaSistema2");
			console.log(datosCurvaSistema2);
			

			cota=parseFloat($("#frm_curvas_de_sistema input[name='cota']").val())-parseFloat($("#frm_curvas_de_sistema input[name='succion2']").val());	
			var frecuencia1 = $("#frm_curvas_de_sistema input[name='frecuencia1']").val();
			var frecuencia2 = $("#frm_curvas_de_sistema input[name='frecuencia2']").val();
			var Qmax =limitesObjeto.limites_graf.x.max;
			if($("input[name=radio_tipo_curva]:checked").val()=="p_operacion"){
				datosCurvaSistema=jccdS(datosarr,cota,parseFloat($("#frm_curvas_de_sistema input[name='cota']").val()),Qmax,frecuencia1,frecuencia2);
			}else{
				datosCurvaSistema=jccdS(datosarr,cota,null,Qmax,frecuencia1,frecuencia2);
			}
			scatterData[4]=datosCurvaSistema;
			curva_de_sistema(datosarr, datosCurvaSistema,3);
			console.log("--datosCurvaSistema3");
			console.log(datosCurvaSistema3);	
			
			
			$('#frm_curvas_de_sistema .boton.nivel_agua').removeClass("off");
			scatterData[6]=interseccion_curva_bomba_sistema(scatterData[3],result_curva_de_bomba,exponente);		
			label_interseccion_curva_bomba_sistema(scatterData[6]);	
			hallar_RPM();
			
			var ctx = document.getElementById('canvas').getContext('2d');
			//var limitesObjeto=null;
			//var scatterData=null;
			
			console.log("--scatterData upd");
			console.log(scatterData);
			
			generarGrafico(ctx,scatterChartData,configuracionGrafico,limitesObjeto,scatterData);

			puntos_calculados
			llenar_tabla_puntos_calculados(puntos_calculados);

			
			guardarDatos();
		},
		function(reason){
			console.log(reason);//ERROR
		}
	);
/*
	var curva_de_bomba_puntos_f=curva_de_bomba(puntos_calculados,exponente);
	curva_de_bomba_puntos_f.then(
		function(result_curva_de_bomba_puntos){
			console.log("--result_curva_de_bomba_puntos");
			console.log(result_curva_de_bomba_puntos);

			scatterData[8]={coord:result_curva_de_bomba_puntos.coord};
			
			override={
				x:{min:0},
				y:{min:0}
			}

			limitesObjeto=limitesbordes_grafico(result_curva_de_bomba_puntos.coord,override,limitesObjeto);
			
			var exponente = $("select[name='exponente'] option:selected").val();
			//var exponente=4;
			
			torre_verificacion_curva(limites_graf.x.max,exponente);
			
			var ctx = document.getElementById('canvas').getContext('2d');
			//var limitesObjeto=null;
			//var scatterData=null;
			
			console.log("--scatterData upd");
			console.log(scatterData);
			
			llenar_tabla_puntos_calculados(result_curva_de_bomba_puntos.coord);
			
			generarGrafico(ctx,scatterChartData,configuracionGrafico,limitesObjeto,scatterData);	
			guardarDatos();
			
			
		},
		function(reason){
			console.log(reason);//ERROR
		}
	);
	*/
}

function llenar_tabla_puntos_calculados(coord){
	console.log("->llenar_tabla_puntos_calculados");
	if(coord.length>0){
		$(coord).each(function(index, element) {
			console.log(element);
		   var div_nodo=$($("skeleton[rel='datos_puntos_calculados']").html());
		   div_nodo.find("span.num_order").text(index+1);
		   div_nodo.find("span.caudal").text((element.Q).toFixed(2));
		   div_nodo.find("span.altura").text((element.H).toFixed(2));
		   $("#puntos_calculados_tabla").append(div_nodo);
		});
	}
}


function curva_de_sistema(datosarr, datosCurvaSistema, n_cota){
	console.log("->curva_de_sistema");
	console.log("--ncota: "+n_cota);
	console.log("--ncota: "+n_cota);
	
	/*
	
	if($("input[name=radio_tipo_curva]:checked").val()=="p_operacion"){
		
		datosarr1=PuntosQH2Object("#frm_curvas_de_sistema input[name='PO_Qt[]'].tuberias","#frm_curvas_de_sistema input[name='PO_Ht[]'].tuberias");
		
		var Q_arr=$("#frm_curvas_de_sistema input[name='PO_Qt[]'].tuberias ");
		//console.log(Q_arr);
		var H_arr=$("#frm_curvas_de_sistema input[name='PO_Ht[]'].tuberias ");
		//console.log(H_arr);	
	}else{
		datosarr1=PuntosQH2Object("#frm_curvas_de_sistema input[name='Qt[]'].tuberias ","#frm_curvas_de_sistema input[name='Ht[]'].tuberias ");
		var Q_arr=$("#frm_curvas_de_sistema input[name='Qt[]'].tuberias ");
		//console.log(Q_arr);
		var H_arr=$("#frm_curvas_de_sistema input[name='Ht[]'].tuberias ");
		//console.log(H_arr);		
	}
	
	
	
	var datosarr=[];
	
	
	$.each( Q_arr, function( key, value ) {
		var tempQ=$(value).val();
		var tempH=$(H_arr[key]).val();
			datosarr[key]={"Q":parseFloat(tempQ),"H":parseFloat(tempH)};
	});

	console.log("datosarr")
	console.log(datosarr);

	*/
	var cota=0;
	
	if(n_cota==1){
		cota=parseFloat($("#frm_curvas_de_sistema input[name='cota']").val());
	}else if (n_cota==2){
		succion=parseFloat($("#frm_curvas_de_sistema input[name='succion1']").val());
		cota=parseFloat($("#frm_curvas_de_sistema input[name='cota']").val())-succion;
		
	}else{
		succion=parseFloat($("#frm_curvas_de_sistema input[name='succion2']").val());
		cota=parseFloat($("#frm_curvas_de_sistema input[name='cota']").val())-succion;		
	}
	console.log("--cota: "+cota);
	
	//var datosCurvaSistema=jccd(datosarr,2,cota);
	
	/*
	if($("input[name=tab_PO]").prop("checked")){
		datosCurvaSistema=jccdS_PO(datosarr,cota,parseFloat($("#frm_curvas_de_sistema input[name='cota']").val()));
	}else{
		datosCurvaSistema=jccdS(datosarr,cota);
	}
	*/
	
	
	if(n_cota==1){
		datosCurvaSistema1=datosCurvaSistema;
	}else if (n_cota==2){
		//if($("input[name=tab_PO]").prop("checked")){
			//datosCurvaSistema2=datosCurvaSistema1
		//}else{
			datosCurvaSistema2=datosCurvaSistema;
		//}
	}else{
		datosCurvaSistema3=datosCurvaSistema;
	}
	
	console.log("--datosCurvaSistema");
	console.log(datosCurvaSistema);
	return datosCurvaSistema
}

async function curva_de_bomba(datosarr,exponente,callback){
		
	let promise = new Promise((resolve, reject) => {
		console.log("->PROMESA curva_de_bomba");
		
		//var datosCurvaBomba_f=jccd(datosarr,exponente);
	
		var frecuencia1 = $("#frm_curvas_de_sistema input[name='frecuencia1']").val();
		var frecuencia2 = $("#frm_curvas_de_sistema input[name='frecuencia2']").val();
		
		var datosCurvaBomba_f=jccd(datosarr,exponente,frecuencia1,frecuencia2,null);
		
		datosCurvaBomba_f.then(function(result_datosCurvaBomba){
			//console.log(result_datosCurvaBomba);
			datosCurvaBomba=result_datosCurvaBomba;
			datosCurvaBombaActualizable=result_datosCurvaBomba;
			
			scatterData[0]=result_datosCurvaBomba;//datosCurvaBomba
			scatterData[1]=result_datosCurvaBomba;//datosCurvaBombaActualizable
		
			console.log(":: FIN PROMESA curva_de_bomba");
			resolve(datosCurvaBomba);			
			
			var datosPuntos=PuntosQH2Object("#frm_curvas_de_sistema  input[name='Q[]'].ingreso_Q_H","#frm_curvas_de_sistema  input[name='H[]'].ingreso_Q_H");
			override={
				x:{min:0},
				y:{min:0}
			}
			limitesObjeto=limitesbordes_grafico(result_datosCurvaBomba.coord,override);
			//limites_grafico(datosarr);
			
			if($(".tab.output_data[page=4]").hasClass("activo")){
				
				var ctx = document.getElementById('canvas').getContext('2d');
				//var limitesObjeto=null;
				//var scatterData=null;
				generarGrafico(ctx,scatterChartData,configuracionGrafico,limitesObjeto,scatterData);
			}		
		});
		

	 });
	let result = await promise;
	return(result);
}

function curva_de_bomba_frec(){
	console.log("->curva_de_bomba_frec");
	
	/*
	var Q_arr=$("#frm_curvas_de_sistema  input[name='Q[]'].ingreso_Q_H");
	//console.log(Q_arr);
	var H_arr=$("#frm_curvas_de_sistema  input[name='H[]'].ingreso_Q_H");
	//console.log(H_arr);	
	
	var datosarr=[];
	var datosarrTMP=[];

	$.each( Q_arr, function( key, value ) {
		
		var tempQ=$(value).val();
		var tempH=$(H_arr[key]).val();
		if(isNaN(parseFloat(tempQ))||isNaN(parseFloat(tempH))){
			
		}else{
			datosarr[key]={"Q":parseFloat(tempQ),"H":parseFloat(tempH)};	
		}
	});	
	*/
	var datosarr=PuntosQH2Object("#frm_curvas_de_sistema  input[name='Q[]'].ingreso_Q_H","#frm_curvas_de_sistema  input[name='H[]'].ingreso_Q_H")
	
	var frecuencia1=parseFloat($("#frm_curvas_de_sistema input[name='frecuencia1']").val());
	var frecuencia2=parseFloat($("#frm_curvas_de_sistema input[name='frecuencia2']").val());
	
	console.log("--frecuencia1: "+frecuencia1);
	console.log("--frecuencia2: "+frecuencia2);

	exponente = $("select[name='exponente'] option:selected").val(); //Worksheets("Tabla").Cells(45, 25) 'es el grado del polinomio a graficar 'para probar al inicio, fijarlo en 2	
	//var datosCurvaBombaActualizable_f=jccd(datosarr,exponente);
	

	var datosCurvaBombaActualizable_f=jccd(datosarr,exponente,frecuencia1,frecuencia2,null);
	
	datosCurvaBombaActualizable_f.then(
		function(result_datosCurvaBombaActualizable){
			console.log("--result_datosCurvaBombaActualizable");
			console.log(result_datosCurvaBombaActualizable);
			
			datosCurvaBombaActualizable=result_datosCurvaBombaActualizable;
			scatterData[1]=result_datosCurvaBombaActualizable;
			
			var tric=3;
			console.log("--datosCurvaBombaActualizable.nB antes del tric");
			console.log(datosCurvaBombaActualizable.nB);
			
			for (let i = exponente; i >=0 ; i--) {
				tric--;
				//nY = nY + nB[i]* Math.pow(nX,(nN - i));
				//console.log(datosCurvaBomba.nB[i]);
				//console.log(i);
				//console.log(tric);
				//console.log(result_datosCurvaBombaActualizable.nB[i]*Math.pow((frecuencia2/frecuencia1),tric));
				datosCurvaBombaActualizable.nB[i]=result_datosCurvaBombaActualizable.nB[i]*Math.pow((frecuencia2/frecuencia1),tric);
			}
			
			//datosCurvaBombaActualizable.nB=datosCurvaBombaActualizableTMP.nB;
			
			console.log("--datosCurvaBombaActualizable.nB");
			console.log(datosCurvaBombaActualizable.nB);
			//console.log("--datosCurvaBombaActualizableTMP.nB");
			//console.log(datosCurvaBombaActualizableTMP.nB);
			
			scatterData[6]=interseccion_curva_bomba_sistema(scatterData[3],datosCurvaBombaActualizable,exponente);	
			label_interseccion_curva_bomba_sistema(scatterData[6]);	
			hallar_RPM();
			
			var ctx = document.getElementById('canvas').getContext('2d');
			//var limitesObjeto=null;
			//var scatterData=null;
			generarGrafico(ctx,scatterChartData,configuracionGrafico,limitesObjeto,scatterData);	
			
		},
		function(reason){
			console.log(reason);//ERROR
		}
	);
	
	
}

//function jccd(datosarr,nExpt,refrescar_grafico,cota){// refresh(boleano) 0 crea nuevo, 1 refresca el creado

//const verificacion_de_curva = () =>


function generarPrevista(){
	console.log("->generarPrevista");
	
	var ctx = document.getElementById('canvasPrevista').getContext('2d');
	
	var coord=(Arr2Coords(PuntosQH2Object(".ingreso_Q_H[name='Q[]']",".ingreso_Q_H[name='H[]']")));
	
	var scatterChartData = {
		datasets: [
			{
				label: 'Prevista',
				borderColor: window.chartColors.blue,
				backgroundColor: color(window.chartColors.red).alpha(0.2).rgbString(),
				data: coord,
				pointRadius: 0, //TBR
				showLine: true, // TBR
				fill: false, //TBR
				hidden: false,
				borderWidth:1,
			},
			{
				label: 'Puntos ingresados',
				borderColor: window.chartColors.gray,
				backgroundColor: color(window.chartColors.gray).alpha(0.2).rgbString(),
				data:coord,
				//pointRadius: 0.5, //TBR
				showLine: false, // TBR
				fill: false, //TBR
			},		
			
		]
	};
	
	var config={
		type: 'scatter',
		data: scatterChartData,
		
		options: {
					animation: {
						duration: 500,
					},
					responsive: true,
					maintainAspectRatio:true,
					title: {
						display: false,
						text: "title"
					},/*
					scales: {
						xAxes: [{
							grid: {
									  display: true,
									  drawBorder: true,
									  drawOnChartArea: true,
									  drawTicks: false,
								},				
						}],
						yAxes: [
							{
							grid: {
									  display: true,
									  drawBorder: true,
									  drawOnChartArea: true,
									  drawTicks: false,
								},	
							
							ticks: {
								
								//min: limites_graf.y.min,
								min: 0,
								max: limites_visuales_graf.y.max,
								
								//stepSize: 10,
							}
						}]
					},*/
					legend: {
						display: false
					},
					/*
					tooltips: {
						callbacks: {
						   label: function(tooltipItem) {
								  return tooltipItem.yLabel;
						   }
						}
					}*/
				}


	};
	console.log("--window.myScatter");
	console.log(typeof(window.myScatter));
	
	if(typeof(window.myScatter)=="undefined"){
		window.myScatter = new Chart(ctx, config);
		//console.log(window.myScatter);
	}else{
		//window.myScatter.data=scatterChartData;
		//console.log("flagHiddenIntersection: "+flagHiddenIntersection);

		window.myScatter.data.datasets.forEach(function(dataset,key) {
			console.log(key);
			console.log(dataset);
			
			if(key==0){
				dataset.data=coord;
			}
			if(key==1){
				dataset.data=coord;
			}	
			

		});
		/*window.myScatter.config.options.scales.yAxes[0].ticks.max = limites_visuales_graf.y.max;
		window.myScatter.config.options.scales.xAxes[0].ticks.max = limites_visuales_graf.x.max;*/
		window.myScatter.update();	
	}
	
}

function generarGrafico(ctx,scatterChartData,config,limitesObjeto,scatterData){
	console.log("->generarGrafico");
	
	
	console.log("--scatterData");
	console.log(scatterData);
	/*
	console.log("--datosPuntos");
	console.log(datosPuntos);
	console.log("--datosInterseccion");
	console.log(datosInterseccion);
	console.log("--datosCurvaBombaActualizable");
	console.log(datosCurvaBombaActualizable);	
	*/
	/*
	var flagHiddenIntersection=true;
	if(datosInterseccion[0].x+datosInterseccion[0].y>0){
		flagHiddenIntersection=false;
	}
	
	console.log(flagHiddenIntersection);
	*/
	
	/*
	console.log("--datosCurvaBomba.coord");
	console.log(datosCurvaBomba.coord);
	
	console.log("--limites_graf");
	console.log(limites_graf);	
	
	console.log("--limites_visuales_graf");
	console.log(limites_visuales_graf);	
	*/
	console.log("--limitesObjeto");
	console.log(limitesObjeto);		
	
	
	
	
	//var ctx = document.getElementById('canvas').getContext('2d');
	//window.myLine = new Chart(ctx, config);
	
	//window.myScatter = Chart.Scatter(ctx, {
	
	/*
	var scatterChartData = {
		datasets: [
			{
				label: 'Curva de bomba',
				borderColor: window.chartColors.blue,
				backgroundColor: color(window.chartColors.red).alpha(0.2).rgbString(),
				data: datosCurvaBomba.coord,
				pointRadius: 0, //TBR
				showLine: true, // TBR
				fill: false, //TBR
				hidden: false,
				borderWidth:1,
			},
			{
				label: 'Curva de bomba (frecuencia actualizable)',
				borderColor: window.chartColors.red,
				backgroundColor: color(window.chartColors.red).alpha(0.2).rgbString(),
				data: datosCurvaBombaActualizable.coord,
				pointRadius: 0, //TBR
				showLine: true, // TBR
				fill: false, //TBR
			},
			{
				label: 'curva 1 de sistema',
				borderColor: window.chartColors.orange,
				backgroundColor: color(window.chartColors.red).alpha(0.2).rgbString(),
				data: datosCurvaSistema1.coord,
				pointRadius: 0, //TBR
				showLine: true, // TBR
				fill: false, //TBR
				borderWidth:1,
			},
			{
				label: 'curva 2 de sistema',
				borderColor: window.chartColors.green,
				backgroundColor: color(window.chartColors.red).alpha(0.2).rgbString(),
				data: datosCurvaSistema2.coord,
				pointRadius: 0, //TBR
				showLine: true, // TBR
				fill: false, //TBR
				
			},			
			{
				label: 'curva 3 de sistema',
				borderColor: window.chartColors.yellow,
				backgroundColor: color(window.chartColors.red).alpha(0.2).rgbString(),
				data: datosCurvaSistema3.coord,
				pointRadius: 0, //TBR
				showLine: true, // TBR
				fill: false, //TBR
				borderWidth:1,
			},			
			{
				label: 'Puntos ingresados',
				borderColor: window.chartColors.gray,
				backgroundColor: color(window.chartColors.gray).alpha(0.2).rgbString(),
				data:datosPuntos,
				//pointRadius: 0.5, //TBR
				showLine: false, // TBR
				fill: false, //TBR
			},
			{
				label: 'Interseccion',
				borderColor: window.chartColors.red,
				backgroundColor: color(window.chartColors.red).alpha(1).rgbString(),
				data:datosInterseccion,
				pointRadius: 5, //TBR
				showLine: false, // TBR
				fill: false, //TBR
				hidden: flagHiddenIntersection,
			},		
		]
	};
	*/
	
	
/*
	console.log("--window.myScatter");
	console.log(window.myScatter);
	console.log(typeof(window.myScatter));
	*/
	if(typeof(window.myScatter1)=="undefined"){
		console.log("window.myScatter NO existe, se creará");
		window.myScatter1 = new Chart(ctx, config);
	}else{
		console.log("window.myScatter existe, se actualizará");
		//window.myScatter.data=scatterChartData;
		//console.log("flagHiddenIntersection: "+flagHiddenIntersection);
		window.myScatter1.data.datasets.forEach(function(dataset,key) {
			dataset.data=scatterData[key].coord;
		});
	}
	window.myScatter1.config.options.scales.yAxes[0].ticks.min = limitesObjeto.limites_visuales_graf.y.min;
	//window.myScatter1.config.options.scales.yAxes[0].ticks.max = limitesObjeto.limites_visuales_graf.y.max;
	window.myScatter1.config.options.scales.xAxes[0].ticks.min = limitesObjeto.limites_visuales_graf.x.min;
	//window.myScatter1.config.options.scales.xAxes[0].ticks.max = limitesObjeto.limites_visuales_graf.x.max;
	window.myScatter1.update();		
}

function titilar_hmax(){
	console.log("->titilar_hmax");
	$("#imagen_guia1>div").addClass("none");
	$(".img_cota.cota0").removeClass("none");
	$(".img_cota.cota1").removeClass("none").addClass("animated flash");
	$("#imagen_guia1").removeClass("none");
}

function titilar_cotamax(){
	console.log("->titilar_cotamax");
	$("#imagen_guia1>div").addClass("none");
	$(".img_cota.cota0").removeClass("none");
	$(".img_cota.cota2").removeClass("none").addClass("animated flash");
	$("#imagen_guia1").removeClass("none");
}

function titilar_perdidaH(){
	console.log("->titilar_perdidaH");
	$("#imagen_guia2>div.img_cota").addClass("none");
	$(".img_cota.cota1").removeClass("none").addClass("animated flash");
}

function titilar_perdidaQ(){
	console.log("->titilar_perdidaQ");
	$("#imagen_guia2>div.img_cota").addClass("none");
	$(".img_cota.cota2").removeClass("none").addClass("animated flash");
}

function guardarDatos(){
	console.log("->guardarDatos");
	var formData = new FormData($("#frm_curvas_de_sistema")[0]);
	var obj = Object.fromEntries(Array.from(formData.keys()).map(key => [key, formData.getAll(key).length > 1 ? formData.getAll(key) : formData.get(key)]))
	console.log(JSON.stringify(obj));
	localStorage.setItem("ilisb_curvas", JSON.stringify(obj));
}

function revisar_pase_tab2(){
	console.log("->revisar_pase_tab2");
	swipe(2);
}

function revisar_pase_tab3(){
	console.log("->revisar_pase_tab3");

	//console.log(datosPrevista.coord);
	
	if(frecuenciaFueraDeRango($("select[name=sfrecuencia1]").val(),$("input[name=rpm1]").val())){
		//$(".question_box[data-rel=rpm_fuera_de_rango]").fadeInFlex();
		var titulo="¡Cuidado!";
		var mensaje="Al parecer la velocidad RPM ingresada no es un valor válido ¿Esta seguro que desea continuar?";
		question_box(mensaje,titulo,rpm_fuera_de_rango_yes,rpm_fuera_de_rango_no);
	}else{
		swipe(4);
	}				
}

function rpm_fuera_de_rango_yes(){
	console.log("->rpm_fuera_de_rango_yes");
	swipe(2);
}

function rpm_fuera_de_rango_no(){
	console.log("->rpm_fuera_de_rango_no");
	$("input[name=rpm1]").focus();
}

