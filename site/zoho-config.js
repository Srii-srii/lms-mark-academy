/*
 * The ONLY file you edit to connect this demo site to Zoho.
 * Paste each snippet exactly as Zoho gives it to you, between the backticks.
 * Leave a value as an empty string to switch that piece off.
 */
window.ZOHO_CONFIG = {
  // Zoho Marketing Automation -> Settings -> Web tracking (website tracking code).
  // Loaded ONLY after the visitor accepts the cookie notice.
  ZMA_TRACKING_SNIPPET: `<script src="https://cdn-in.pagesense.io/js/sritharun251/b3646d8051b54ebaa6dd42da77252d2f.js"></script>`,

  // Zoho Marketing Automation -> sign-up form -> Embed code (HTML/JS embed).
  // Rendered inside the "Join the academy" section on the home page.
  ZMA_SIGNUP_FORM_EMBED: String.raw`<!--Zoho Marketing Automation Web-Optin Form's Header Code Starts Here-->

<script type="text/javascript" src="https://ma.zoho.in/js/optin.min.js" onload="setupSF('sf3z435f3ea722ad21182e69a7eb2734a1708cb5c4af8ed496968849b21383b26d89','ZCFORMVIEW',false,'light')"></script>
<script type="text/javascript">
	function runOnFormSubmit_sf3z435f3ea722ad21182e69a7eb2734a1708cb5c4af8ed496968849b21383b26d89(th){
		/*Before submit, if you want to trigger your event, "include your code here"*/
	};
</script>

<style>
@media only screen and (max-width: 319px){
#zcOptinSuccessPopup{
width:100% !important;
max-width:260px;
top:24% !important;
left:30% !important;
}
#THANKS_PAGE_BODY_PARENT{
width:100% !important;
}
#THANKS_PAGE_CONTAINER{
padding:0px !important;
}
#THANKSPAGE{
padding:10px !important;
}
#THANKS_PAGE_BODY{
padding:20px !important;
}
}
/*Major Mobiles*/
@media screen and (min-width: 320px) and (max-width: 580px){
#zcOptinSuccessPopup{
width:100% !important;
max-width:220px;
top:5% !important;
left:10% !important;
}
#THANKS_PAGE_BODY_PARENT{
width:100% !important;
}
#THANKS_PAGE_CONTAINER{
padding:0px !important;
}
#THANKSPAGE{
padding:10px !important;
}
#THANKS_PAGE_BODY{
padding:20px !important;
}
}
/*Nexus and iPhone 6,6s*/ 
@media screen and (min-width: 374px) and (max-width: 680px){
#zcOptinSuccessPopup{
width:100% !important;
max-width:220px;
top:5% !important;
left:18% !important;
}
#THANKS_PAGE_BODY_PARENT{
width:100% !important;
}
#THANKS_PAGE_CONTAINER{
padding:0px !important;
}
#THANKSPAGE{
padding:10px !important;
}
#THANKS_PAGE_BODY{
padding:20px !important;
}
}
@media screen and (min-width:581px) and (max-width: 767px){
#zcOptinSuccessPopup{
width:100% !important;
max-width:500px;
top:24% !important;
left:6% !important;
}
#THANKS_PAGE_BODY_PARENT{
width:100% !important;
}
#THANKS_PAGE_CONTAINER{
padding:0px !important;
}
#THANKSPAGE{
padding:10px !important;
}
#THANKS_PAGE_BODY{
padding:20px !important;
}
}
/* Desktops and laptops ----------- */
@media only screen  and (min-width : 1025px) {
#zcOptinSuccessPopup{
width:100% !important;
max-width:700px;
top:24% !important;
left:21% !important;
}
#THANKS_PAGE_BODY_PARENT{
width:100% !important;
}
#THANKS_PAGE_CONTAINER{
padding:0px !important;
}
#THANKSPAGE{
padding:10px !important;
}
#THANKS_PAGE_BODY{
padding:20px !important;
}
}
@media only screen and (min-width:1200) and (max-width: 1500px){
#zcOptinSuccessPopup{
width:100% !important;
max-width:700px;
top:24% !important;
left:20% !important;
}
#THANKS_PAGE_BODY_PARENT{
width:100% !important;
}
#THANKS_PAGE_CONTAINER{
padding:0px !important;
}
#THANKSPAGE{
padding:10px !important;
}
#THANKS_PAGE_BODY{
padding:20px !important;
}
}
@media only screen and (min-width:1501px) and (max-width: 1700px){
#zcOptinSuccessPopup{
width:100% !important;
max-width:700px;
top:24% !important;
left:25% !important;
}
#THANKS_PAGE_BODY_PARENT{
width:100% !important;
}
#THANKS_PAGE_CONTAINER{
padding:0px !important;
}
#THANKSPAGE{
padding:10px !important;
}
#THANKS_PAGE_BODY{
padding:20px !important;
}
}
/* Large Screens */
@media only screen  and (min-width : 1824px) {
#zcOptinSuccessPopup{
width:100% !important;
max-width:700px;
top:24% !important;
left:30% !important;
}
#THANKS_PAGE_BODY_PARENT{
width:100% !important;
}
#THANKS_PAGE_CONTAINER{
padding:0px !important;
}
#THANKSPAGE{
padding:10px !important;
}
#THANKS_PAGE_BODY{
padding:20px !important;
}
}
/* iPads*/
@media only screen and (min-width : 768px) and (max-width : 1024px){
#zcOptinSuccessPopup{
width:100% !important;
max-width:600px;
top:14% !important;
left:18.7% !important;
}
#THANKS_PAGE_BODY_PARENT{
width:100% !important;
}
#THANKS_PAGE_CONTAINER{
padding:0px !important;
}
#THANKSPAGE{
padding:10px !important;
}
#THANKS_PAGE_BODY{
padding:20px !important;
}
}
/* #customForm
{
width:100%;
} */
#customForm > div
{
margin: 0 auto
}
</style>

<!--Zoho Marketing Automation Web-Optin Form's Header Code Ends Here--><!--Zoho Marketing Automation Web-Optin Form Starts Here-->


<div name="signupFormContainer">
	<input type="hidden" id="signupTmplName" value="large_form_1">
	<input type="hidden" value="0" id="recapThemeOptin">
	<input type="hidden" id="orgNameFull" value="Self">
	<div id="sf3z435f3ea722ad21182e69a7eb2734a1708cb5c4af8ed496968849b21383b26d89" data-type="signupform">
		<div id="customForm">
			<input type="hidden" id="recapTheme" value="0">
			<input type="hidden" id="isRecapIntegDone" value="false">
			
			<input type="hidden" id="signupFormMode" value="">
			<input type="hidden" id="signupFormType" value="LargeForm_Vertical">
			<input type="hidden" id="recapModeTheme" value=""><input type="hidden" id="signupFormMode" value="">
			<div name="SIGNUP_PAGE" class="large_form_1_css" id="SIGNUP_PAGE" style="padding: 30px; background-color: rgb(137, 217, 242); font-family: Arial; color: rgb(255, 255, 255); text-align: center; font-size: 14px; opacity: 0.936886;">
				<div name="" changeid="" changename="" style="margin:0px auto">
					<div id="imgBlock" name="LOGO_DIV" logo="true" style="width: 600px; margin: 0px auto; padding-bottom: 10px; text-align: left; padding-top: 10px;"></div>
				</div>
				<br>
				<div id="signupMainDiv" style="margin: 0px auto; width: 100%; min-width: 230px; max-width: 600px;" name="SIGNUPFORM" changeid="SIGNUPFORM" changename="SIGNUPFORM">
					<div>
						<div style="position:relative;">
							<div id="Zc_SignupSuccess" style="display:none;position:absolute;margin-left:4%;width:90%;background-color: white; padding: 3px; border: 3px solid rgb(194, 225, 154);  margin-top: 10px;margin-bottom:10px;word-break:break-all">
								<table width="100%" cellpadding="0" cellspacing="0" border="0">
									<tbody>
										<tr>
											<td width="10%">
												<img class="successicon" src="https://ma.zoho.in/images/challangeiconenable.jpg" align="absmiddle" alt="thumsup">
											</td>
											<td>
												
							<span id="signupSuccessMsg" style="color: rgb(73, 140, 132); font-family: sans-serif; font-size: 14px;word-break:break-word">&nbsp;&nbsp;Thank you for Signing Up</span>
						
											</td>
										</tr>
									</tbody>
								</table>
							</div>
						</div>
						<form method="POST" id="zcampaignOptinForm" style="margin:0px;" action="https://haun-zgp4.maillist-manage.in/weboptin.zc" target="_zcSignup">
							<div id="SIGNUP_BODY_ALL" name="SIGNUP_BODY_ALL" style="border: 1px rgb(218, 216, 216);">
								<h1 style="color: rgb(255, 255, 255); font-size: 17px; font-family: Arial; margin: 0px; text-align: left; padding: 20px; background-color: rgb(21, 111, 137); word-break: break-word; border-color: rgb(21, 111, 137); border-width: 1px; border-style: none;" id="SIGNUP_HEADING" name="SIGNUP_HEADING" changeid="SIGNUP_MSG" changetype="SIGNUP_HEADER">Join LMS-Mark Academy</h1>
								<div style="padding: 20px; text-align: center; background-color: rgb(255, 255, 255); font-family: Arial; color: rgb(68, 68, 68); bottom: 2px; font-size: 11px; opacity: 1;" id="SIGNUP_BODY" name="SIGNUP_BODY">
									<div style="margin:0px auto;text-align:left;">
										<div style="line-height:1.6;" class="" changeid="SIGNUP_MSG" id="SIGNUP_DESCRIPTION" changetype="SIGNUP_DESCRIPTION">Get course updates and free webinars. Tick the channels you want. Unsubscribe anytime.</div>
										<div style="display:none;background-color:#FFEBE8;padding:10px 10px; color:#d20000; font-size:11px; margin:10px 0px;border:solid 1px #ffd9d3; margin-top:20px;" id="errorMsgDiv">&nbsp;&nbsp;Please correct the marked field(s) below.</div>
										<div>
											<div style="font-size:12px; margin-top:10px;" name="fieldsdivSf" class="zcsffieldsdiv">
												<div style="padding:10px 0px 10px 0px;">
													<div style="">
														<div style="width: 130px; float: left; margin-top: 5px; margin-right: 5px; text-align: left; font-family: Arial; color: rgb(51, 51, 51); font-size: 12px;" name="SIGNUP_FORM_LABEL">Lead Email&nbsp;
															<span name="SIGNUP_REQUIRED" style="color:#B40000;font-size:11px;font-family:Arial;">*</span>
														</div>
														<div style="width:60%; float:left;  min-width:170px; max-width:70%;" class="zcinputbox"><!-- check to mark emailid field as type email, and other mandatory fields as type required -->
															<input name="CONTACT_EMAIL" changeitem="SIGNUP_FORM_FIELD" style="height:28px;padding:2px; width:97%;color:#444444;background-color:#fff;font-family:;border-width:1px;border:solid 1px #dedede;font-family:Arial;font-size:12px;-moz-box-sizing:border-box;-webkit-box-sizing:border-box;-o-box-sizing:border-box;box-sizing:border-box;" maxlength="100" type="email">
															<span style="display:none" id="dt_CONTACT_EMAIL">1,true,6,Lead Email,2</span>
														</div>
													</div>
													
													
													
															
													
															
													<div style="clear:both"></div>
												
														
												
														
												
												
												</div>
												<div style="padding:10px 0px 10px 0px;">
													<div style="">
														<div style="width: 130px; float: left; margin-top: 5px; margin-right: 5px; text-align: left; font-family: Arial; color: rgb(51, 51, 51); font-size: 12px;" name="SIGNUP_FORM_LABEL">First Name&nbsp;</div>
														<div style="width:60%; float:left;  min-width:170px; max-width:70%;" class="zcinputbox"><!-- check to mark emailid field as type email, and other mandatory fields as type required -->
															<input name="FIRSTNAME" changeitem="SIGNUP_FORM_FIELD" style="height:28px;padding:2px; width:97%;color:#444444;background-color:#fff;font-family:;border-width:1px;border:solid 1px #dedede;font-family:Arial;font-size:12px;-moz-box-sizing:border-box;-webkit-box-sizing:border-box;-o-box-sizing:border-box;box-sizing:border-box;" maxlength="100" type="text">
															<span style="display:none" id="dt_FIRSTNAME">1,false,1,First Name,2</span>
														</div>
													</div><div style="clear:both"></div></div>
												<div style="padding:10px 0px 10px 0px;">
													<div style="">
														<div style="width: 130px; float: left; margin-top: 5px; margin-right: 5px; text-align: left; font-family: Arial; color: rgb(51, 51, 51); font-size: 12px;" name="SIGNUP_FORM_LABEL">Mobile&nbsp;</div>
														<div style="width:60%; float:left;  min-width:170px; max-width:70%;" class="zcinputbox"><!-- check to mark emailid field as type email, and other mandatory fields as type required -->
															<input name="MOBILE" changeitem="SIGNUP_FORM_FIELD" style="height:28px;padding:2px; width:97%;color:#444444;background-color:#fff;font-family:;border-width:1px;border:solid 1px #dedede;font-family:Arial;font-size:12px;-moz-box-sizing:border-box;-webkit-box-sizing:border-box;-o-box-sizing:border-box;box-sizing:border-box;" maxlength="20" type="text">
															<span style="display:none" id="dt_MOBILE">1,false,1,Mobile,2</span>
														</div>
													</div><div style="clear:both"></div></div>
												<div style="padding:10px 0px 10px 0px;">
													<div style="">
														<div>
															<div style="width: 130px; float: left; margin-top: 5px; text-align: left; margin-right: 5px; font-family: Arial; color: rgb(51, 51, 51); font-size: 12px;" name="SIGNUP_FORM_LABEL">WhatsApp opt-in&nbsp;</div>
															<div style="width:60%; float:left;  min-width:170px;  max-width:70%;" class="zcinputbox">
																<input name="CONTACT_CF36" type="checkbox" zc_display_name="WhatsApp opt-in" value="" style="padding-left:10px;padding-right:10px; margin-top:5px;">
																<span style="display:none" id="dt_CONTACT_CF36">4,false,4,WhatsApp opt-in,2</span>
															</div><div style="clear:both"></div></div>
													</div><div style="clear:both"></div></div>
												<div style="padding:10px 0px 10px 0px;">
													<div style="">
														<div>
															<div style="width: 130px; float: left; margin-top: 5px; text-align: left; margin-right: 5px; font-family: Arial; color: rgb(51, 51, 51); font-size: 12px;" name="SIGNUP_FORM_LABEL">SMS opt-in&nbsp;</div>
															<div style="width:60%; float:left;  min-width:170px;  max-width:70%;" class="zcinputbox">
																<input name="CONTACT_CF37" type="checkbox" zc_display_name="SMS opt-in" value="" style="padding-left:10px;padding-right:10px; margin-top:5px;">
																<span style="display:none" id="dt_CONTACT_CF37">4,false,4,SMS opt-in,2</span>
															</div><div style="clear:both"></div></div>
													</div><div style="clear:both"></div></div>
											</div><!-- Captcha for Signup End--><!-- Other Lists Subscription Start--><!-- Other Lists Subscription End-->
											<div style=" border-bottom:#ebebeb dotted 1px; margin-top:10px; clear:both;"></div>
											<div id="REQUIRED_FIELD_TEXT" changetype="REQUIRED_FIELD_TEXT" name="SIGNUP_REQUIRED" style="color:#B40000;font-size:11px;font-family:Arial; padding:10px 10px 10px 0px; ">*Required fields</div>
											<div style="padding:10px; text-align:center;">
												<input type="button" action="Save" id="zcWebOptin" name="SIGNUP_SUBMIT_BUTTON" changetype="SIGNUP_SUBMIT_BUTTON_TEXT" style="cursor: pointer; appearance: none; border-radius: 3px; background-position: center bottom; background-repeat: repeat-x; outline: none medium; padding: 5px 15px; text-align: center; color: rgb(255, 255, 255); font-size: 14px; background-color: rgb(142, 185, 52); border-style: solid; border-color: rgb(142, 185, 52); font-family: Arial; border-width: 5px; white-space: normal;" value="Join free">
											</div>
										</div>
									</div>
								</div><!-- Do not edit the below Zoho Campaigns hidden tags -->
								<input type="hidden" id="fieldBorder" value="rgb(222, 222, 222)" onload="">
								<input type="hidden" name="zc_trackCode" id="zc_trackCode" value="" onload="">
								<input type="hidden" name="viewFrom" id="viewFrom" value="URL_ACTION">
								<input type="hidden" id="submitType" name="submitType" value="optinCustomView">
								<input type="hidden" id="lD" name="lD" value="">
								<input type="hidden" name="emailReportId" id="emailReportId" value="">
								<input type="hidden" name="zx" id="cmpZuid" value="1dfdb94356">
								<input type="hidden" name="zcvers" value="2.0">
								<input type="hidden" name="oldListIds" id="allCheckedListIds" value="">
								<input type="hidden" id="mode" name="mode" value="OptinCreateView">
								<input type="hidden" id="zcld" name="zcld" value="">
								<input type="hidden" id="zctd" name="zctd" value="">
								<input type="hidden" id="document_domain" value="ma.zoho.in">
								<input type="hidden" id="zc_Url" value="haun-zgp4.maillist-manage.in">
								<input type="hidden" id="new_optin_response_in" value="0">
								<input type="hidden" id="duplicate_optin_response_in" value="0">
								<input type="hidden" id="zc_formIx" name="zc_formIx" value="3z435f3ea722ad21182e69a7eb2734a1708cb5c4af8ed496968849b21383b26d89"><!-- End of the campaigns hidden tags --></div>
						</form>
					</div>
				</div>
			</div>
			<input type="hidden" id="isCaptchaNeeded" value="false">
			<input type="hidden" id="superAdminCap" value="0">
			<img src="https://haun-zgp4.maillist-manage.in/images/spacer.gif" id="refImage" onload="referenceSetter(this)" style="display:none;">
		</div>
	</div>
	<div style="position:relative;">
		<div id="Zc_SignupSuccess" style="display:none;position:absolute;margin-left:4%;width:90%;background-color: white; padding: 3px; border: 3px solid rgb(194, 225, 154);margin-bottom:10px;word-break: break-all;">
			<table width="100%" cellpadding="0" cellspacing="0" border="0">
				<tbody>
					<tr>
						<td width="10%">
							<img class="successicon" src="//campaigns.zoho.in/images/challangeiconenable.jpg" align="absmiddle">
						</td>
						<td><span id="signupSuccessMsg" style="color: rgb(73, 140, 132); font-family: sans-serif; font-size: 14px;word-break:break-word">&nbsp;&nbsp;Thank you for Signing Up</span></td>
					</tr>
				</tbody>
			</table>
		</div>
	</div>
	
<div id="zcOptinOverLay" oncontextmenu="return false" style="display:none;text-align: center; background-color: rgb(0, 0, 0); opacity: 0.5; z-index: 100; position: fixed; width: 100%; top: 0px; left: 0px; height: 988px;"></div>
	<div id="zcOptinSuccessPopup" style="margin:0px auto;display:none;z-index: 9999;width: 800px; height:24%;top: 84px;position: fixed; left: 26%;background-color: #FFFFFF;border-color: #E6E6E6; border-style: solid; border-width: 1px;  box-shadow: 0 1px 10px #424242;padding: 35px;">
		<span style="position: absolute;top: -16px;right: -14px;z-index:1;cursor: pointer;" onclick="closeSuccessPopup()">
			<img src="//campaigns.zoho.in/images/videoclose.png">
		</span>
		
	<div id="zcOptinSuccessPanel"></div>

	</div>
</div><div id="zcOptinOverLay" oncontextmenu="return false" style="display:none;text-align: center; background-color: rgb(0, 0, 0); opacity: 0.5; z-index: 100; position: fixed; width: 100%; top: 0px; left: 0px; height: 988px;"></div>
<div id="zcOptinSuccessPopup" style="display:none;z-index: 9999;width: 800px; height: 40%;top: 84px;position: fixed; left: 26%;background-color: #FFFFFF;border-color: #E6E6E6; border-style: solid; border-width: 1px;  box-shadow: 0 1px 10px #424242;padding: 35px;">
	<span style="position: absolute;top: -16px;right:-14px;z-index:99999;cursor: pointer;" id="closeSuccess">
		<img src="https://ma.zoho.in/images/videoclose.png" alt="close">
	</span><div id="zcOptinSuccessPanel"></div></div>

<!--Zoho Marketing Automation Web-Optin Form Ends Here-->`,

  // Zoho SalesIQ -> Settings -> Brands -> Installation -> website code.
  // Functional chat, loaded on every page.
  SALESIQ_WIDGET_SNIPPET: String.raw`<script>window.$zoho=window.$zoho || {};$zoho.salesiq=$zoho.salesiq||{ready:function(){}}</script><script id="zsiqscript" src="https://salesiq.zohopublic.in/widget?wc=siqe033b24f981cca0d3b5d75ba37ae8869d9701ec17be636e8670be51f2c7322ad" defer></script>`,
};
