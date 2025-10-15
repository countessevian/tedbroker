const handleThemeUpdate = (cssVars) => {
    const root = document.querySelector(':root');
    const keys = Object.keys(cssVars);
    keys.forEach(key => {
        root.style.setProperty(key, cssVars[key]);
    });
}

function dynamicPrimaryColor(primaryColor) {
    'use strict'
    
    primaryColor.forEach((item) => {
        item.addEventListener('input', (e) => {
            const cssPropName = `--primary-${e.target.getAttribute('data-id')}`;
            const cssPropName1 = `--primary-${e.target.getAttribute('data-id1')}`;
            const cssPropName2 = `--primary-${e.target.getAttribute('data-id2')}`;
            handleThemeUpdate({
                [cssPropName]: e.target.value,
                // 95 is used as the opacity 0.95  
                [cssPropName1]: e.target.value + 95,
                [cssPropName2]: e.target.value,
            });
        });
    });
}
function dynamicBackgroundColor(BackgroundColor) {
    'use strict'
    
    BackgroundColor.forEach((item) => {
        item.addEventListener('input', (e) => {
            const cssPropName = `--dark-${e.target.getAttribute('data-id3')}`;
            const cssPropName1 = `--dark-${e.target.getAttribute('data-id4')}`;
            handleThemeUpdate({
                [cssPropName]: e.target.value + 'dd',
                [cssPropName1]: e.target.value,
            });
        });
    });
}

$(function () {
    'use strict'

    // Light theme color picker 
    const dynamicPrimaryLight = document.querySelectorAll('input.color-primary-light');
    const dynamicBgColor = document.querySelectorAll('input.background-primary-light');

    // themeSwitch(LightThemeSwitchers);
    dynamicPrimaryColor(dynamicPrimaryLight);
    dynamicBackgroundColor(dynamicBgColor);

    localStorageBackup();
        
});

function localStorageBackup() {
    'use strict'

    // if there is a value stored, update color picker and background color
    // Used to retrive the data from local storage
    if (localStorage.dashplexprimaryColor) {
        // document.getElementById('colorID').value = localStorage.dashplexprimaryColor;
        document.querySelector('html').style.setProperty('--primary-bg-color', localStorage.dashplexprimaryColor);
        document.querySelector('html').style.setProperty('--primary-bg-hover', localStorage.dashplexprimaryHoverColor);
        document.querySelector('html').style.setProperty('--primary-bg-border', localStorage.dashplexprimaryBorderColor);
    }
    
    if (localStorage.dashplexbgColor) {
        document.body.classList.add('dark-theme');
        document.body.classList.remove('light-theme');
        $('#myonoffswitch2').prop('checked', true);
        $('#myonoffswitch5').prop('checked', true);
        $('#myonoffswitch8').prop('checked', true);
        // document.getElementById('bgID').value = localStorage.dashplexthemeColor;
        document.querySelector('html').style.setProperty('--dark-body', localStorage.dashplexbgColor);
        document.querySelector('html').style.setProperty('--dark-theme', localStorage.dashplexthemeColor);
    }
    if(localStorage.dashplexlightMode){
        document.querySelector('body')?.classList.add('light-theme');
		document.querySelector('body')?.classList.remove('dark-theme');
        $('#myonoffswitch1').prop('checked', true);
        $('#myonoffswitch3').prop('checked', true);
        $('#myonoffswitch6').prop('checked', true);
    }
    if(localStorage.dashplexdarktheme){
        document.querySelector('body')?.classList.add('dark-theme');
    }
    if(localStorage.dashplexleftmenu){
        document.querySelector('body').classList.add('leftmenu')
    }
    if(localStorage.dashplexhorizontalmenu){
        document.querySelector('body').classList.add('horizontalmenu')
    }
    if(localStorage.dashplexhorizontalmenuHover){
        document.querySelector('body').classList.add('horizontalmenu-hover')
    }
    if(localStorage.dashplexrtl){
        document.querySelector('body').classList.add('rtl')
    }
    
    if(localStorage.dashplexclosedmenu){
        document.querySelector('body').classList.add('closed-menu')
    }

    if(localStorage.dashplexicontextmenu){
        document.querySelector('body').classList.add('icontext-menu');
        icontext();
    }

    if(localStorage.dashplexsideiconmenu){
        document.querySelector('body').classList.add('icon-overlay')
        document.querySelector('body').classList.add('main-sidebar-hide')
    }

    if(localStorage.dashplexhoversubmenu){
        document.querySelector('body').classList.add('hover-submenu')
        document.querySelector('body').classList.add('main-sidebar-hide')
    }

    if(localStorage.dashplexhoversubmenu1){
        document.querySelector('body').classList.add('hover-submenu1')
        document.querySelector('body').classList.add('main-sidebar-hide')
    }

    if(localStorage.dashplexlightmenu){
        document.querySelector('body').classList.add('light-menu')
        document.querySelector('body').classList.remove('dark-menu')
    }

    if(localStorage.dashplexcolormenu){
        document.querySelector('body').classList.add('color-menu')
        document.querySelector('body').classList.remove('dark-menu')
    }

    if(localStorage.dashplexdarkmenu){
        document.querySelector('body').classList.add('dark-menu')
    }

    if(localStorage.dashplexlightheader){
        document.querySelector('body').classList.add('header-light')
    }

    if(localStorage.dashplexcolorheader){
        document.querySelector('body').classList.add('color-header')
    }

    if(localStorage.dashplexdarkheader){
        document.querySelector('body').classList.add('header-dark')
    }
}

// triggers on changing the color picker
function changePrimaryColor() {
    'use strict';
    checkOptions();

    var userColor = document.getElementById('colorID').value;
    localStorage.setItem('dashplexprimaryColor', userColor);
    // to store value as opacity 0.95 we use 95
    localStorage.setItem('dashplexprimaryHoverColor', userColor + 95);
    localStorage.setItem('dashplexprimaryBorderColor', userColor);

    names()
}
// triggers on changing the color picker
function changeBackgroundColor() {

    var userColor = document.getElementById('bgID').value;
    localStorage.setItem('dashplexbgColor', userColor + 'dd');
    localStorage.setItem('dashplexthemeColor', userColor);
    names()
  
    document.body.classList.add('dark-theme');
    document.body.classList.remove('light-theme');
    $('#myonoffswitch2').prop('checked', true);
    $('#myonoffswitch5').prop('checked', true);
    $('#myonoffswitch8').prop('checked', true);
  
    localStorage.setItem("dashplexdarkMode", true);
    names();
  }
  

// to check the value is hexa or not
const isValidHex = (hexValue) => /^#([A-Fa-f0-9]{3,4}){1,2}$/.test(hexValue)

const getChunksFromString = (st, chunkSize) => st.match(new RegExp(`.{${chunkSize}}`, "g"))
    // convert hex value to 256
const convertHexUnitTo256 = (hexStr) => parseInt(hexStr.repeat(2 / hexStr.length), 16)
    // get alpha value is equla to 1 if there was no value is asigned to alpha in function
const getAlphafloat = (a, alpha) => {
        if (typeof a !== "undefined") { return a / 255 }
        if ((typeof alpha != "number") || alpha < 0 || alpha > 1) {
            return 1
        }
        return alpha
    }
    // convertion of hex code to rgba code 
function hexToRgba(hexValue, alpha) {
    'use strict'

    if (!isValidHex(hexValue)) { return null }
    const chunkSize = Math.floor((hexValue.length - 1) / 3)
    const hexArr = getChunksFromString(hexValue.slice(1), chunkSize)
    const [r, g, b, a] = hexArr.map(convertHexUnitTo256)
    return `rgba(${r}, ${g}, ${b}, ${getAlphafloat(a, alpha)})`
}


let myVarVal

function names() {
    'use strict'

    let primaryColorVal = getComputedStyle(document.documentElement).getPropertyValue('--primary-bg-color').trim();

    //get variable
    myVarVal = localStorage.getItem("dashplexprimaryColor")  || primaryColorVal;
    // index charts
    if(document.querySelector('#salessummary') !== null){
        index();
    }
	if(document.querySelector('#sales-summary') !== null){
        index2();
    }
	if(document.querySelector('#revenuemorrischart') !== null){
        morrisFn();
    }

    let colorData1 = hexToRgba(myVarVal || primaryColorVal , 0.1)
    document.querySelector('html').style.setProperty('--primary01', colorData1);

    let colorData2 = hexToRgba(myVarVal || primaryColorVal , 0.2)
    document.querySelector('html').style.setProperty('--primary02', colorData2);

    let colorData3 = hexToRgba(myVarVal || primaryColorVal , 0.3)
    document.querySelector('html').style.setProperty('--primary03', colorData3);

    let colorData4 = hexToRgba(myVarVal || primaryColorVal , 0.4)
    document.querySelector('html').style.setProperty('--primary04', colorData4);

    let colorData5 = hexToRgba(myVarVal || primaryColorVal , 0.5)
    document.querySelector('html').style.setProperty('--primary05', colorData5);

    let colorData6 = hexToRgba(myVarVal || primaryColorVal , 0.6)
    document.querySelector('html').style.setProperty('--primary06', colorData6);

    let colorData7 = hexToRgba(myVarVal || primaryColorVal , 0.7)
    document.querySelector('html').style.setProperty('--primary07', colorData7);

    let colorData8 = hexToRgba(myVarVal || primaryColorVal , 0.8)
    document.querySelector('html').style.setProperty('--primary08', colorData8);

    let colorData9 = hexToRgba(myVarVal || primaryColorVal , 0.9)
    document.querySelector('html').style.setProperty('--primary09', colorData9);

    let colorData05 = hexToRgba(myVarVal || primaryColorVal , 0.05)
    document.querySelector('html').style.setProperty('--primary005', colorData05);

}

names()
 