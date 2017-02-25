function httpGetAsync(theUrl, callback)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    }
    xmlHttp.open("GET", theUrl, true); // true for asynchronous 
    xmlHttp.send(null);
}

function cb(_nothing){

}

function detected(text){
	httpGetAsync("/bot/"+text, cb)
}

function detect_bot(){
	bot = null;
	do{
		if(!!window._phantom ){
			bot="phantom";
			break;
		}
		if(!!window.callPhantom){
			bot="phantom";
			break;
		}
		if(!!window.__phantomas){
			bot="phantom";
			break;
		}
		if(!Function.prototype.bind){
			bot="phantom";
			break;
		}
		if(!!window.Buffer){
			bot="nodejs";
			break;
		}
		if(!!window.emit ){
			bot="couchjs";
			break;
		}
		if(!!window.spawn){
			bot="rhino"
			break;
		}
		if(!!window.webdriver){
			bot="selenium"
			break;
		}
		if(!!window.domAutomation){
			bot="chromium"
			break;
		}
		if(!!window.domAutomationController){
			bot="chromium"
			break;
		}
	} while(0);
	if(bot) detected(bot);
}

if(window.addEventListener){
  window.addEventListener('load', detect_bot)
}else{
  window.attachEvent('onload', detect_bot)
}