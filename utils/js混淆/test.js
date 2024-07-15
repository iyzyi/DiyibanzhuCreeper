const jsdom = require("jsdom");
const { JSDOM } = jsdom;

function hello() {
    const dom = new JSDOM(`<!DOCTYPE html><p>Hello world</p>`);
    console.log(dom.window.document.querySelector("p").textContent); 
    return dom.window.document.querySelector("p").textContent;
}

hello();

// node test.js