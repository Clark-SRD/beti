var TITLE = 'Building Enclosure Tests Tool';

const createMenu = () => {
  const menu = SpreadsheetApp.getUi()
    .createMenu(TITLE)
    .addItem(TITLE, 'showConfig') // This opens the sidebar
    .addToUi();
  menu.addToUi();
};

const onOpen = () => {
  createMenu();
};

const showConfig = () => {
  const sheet = SpreadsheetApp.getActiveSpreadsheet();
  const props = PropertiesService.getDocumentProperties().getProperties();
  const template = HtmlService.createTemplateFromFile('sidebar');
  const htmlOutput = template.evaluate();
  htmlOutput.setTitle(TITLE).setWidth(300);
  SpreadsheetApp.getUi().showSidebar(htmlOutput);
};

function writeDataToSheet(data) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var lastRow = sheet.getLastRow() + 1;
    for (var i = 0; i < data.length; i++) {
      sheet.getRange(lastRow + i, 1, 1, data[i].length).setValues([data[i]]);
    }
    Logger.log("Data successfully written to the sheet.");
  } catch (error) {
    Logger.log("An error occurred: " + error.toString());
  }
}
