const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  BorderStyle, WidthType, AlignmentType, ImageRun, ShadingType,
  VerticalAlign,
} = require("docx");

const LOGO_PATH = path.join(__dirname, "..", "assets", "logo.png");
const BRAND_DARK = "1B3A63";
const BRAND_BLUE = "2E7BD6";
const GREY = "6B7280";
const LIGHT_FILL = "F2F5FA";
const CJK_FONT = { ascii: "Calibri", hAnsi: "Calibri", eastAsia: "Microsoft JhengHei", cs: "Calibri" };

const PAGE_WIDTH_DXA = 11907; // A4
const MARGIN_DXA = 1080;      // 0.75"
const CONTENT_WIDTH = PAGE_WIDTH_DXA - MARGIN_DXA * 2;

function noBorders() {
  const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  return { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none };
}

function cell(children, opts = {}) {
  return new TableCell({
    children,
    width: { size: opts.width, type: WidthType.DXA },
    borders: opts.borders || noBorders(),
    shading: opts.shading ? { type: ShadingType.CLEAR, fill: opts.shading, color: "auto" } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
  });
}

function labelValue(label, value, bold = false) {
  return new Paragraph({
    alignment: AlignmentType.RIGHT,
    spacing: { after: 20 },
    children: [
      new TextRun({ text: label + "  ", color: GREY, size: 18 }),
      new TextRun({ text: value, bold, size: 20, color: BRAND_DARK }),
    ],
  });
}

function buildInvoice({ invoiceNo, invoiceDate, billTo, items, total, termsUrl, outPath }) {
  const logoBuffer = fs.readFileSync(LOGO_PATH);

  const headerTable = new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: [3400, CONTENT_WIDTH - 3400],
    borders: noBorders(),
    rows: [new TableRow({
      children: [
        cell([new Paragraph({
          children: [new ImageRun({ type: "png", data: logoBuffer, transformation: { width: 168, height: 112 } })],
        })], { width: 3400 }),
        cell([
          new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "INVOICE", bold: true, size: 40, color: BRAND_DARK })] }),
          new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { before: 40 }, children: [new TextRun({ text: "Dreambiggg Co. Ltd.", size: 20, color: GREY })] }),
          new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "info@dreambiggg.app  |  www.dreambiggg.app", size: 18, color: GREY })] }),
        ], { width: CONTENT_WIDTH - 3400 }),
      ],
    })],
  });

  const ruleParagraph = new Paragraph({
    spacing: { before: 200, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: BRAND_BLUE, space: 4 } },
    children: [],
  });

  const billToLines = billTo.map((line, i) => new Paragraph({
    spacing: { after: 20 },
    children: [new TextRun({ text: line, bold: i === 0, size: i === 0 ? 22 : 20, color: i === 0 ? BRAND_DARK : GREY, font: CJK_FONT })],
  }));

  const metaTable = new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: [Math.round(CONTENT_WIDTH * 0.55), CONTENT_WIDTH - Math.round(CONTENT_WIDTH * 0.55)],
    borders: noBorders(),
    rows: [new TableRow({
      children: [
        cell([
          new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: "BILL TO", bold: true, size: 18, color: GREY })] }),
          ...billToLines,
        ], { width: Math.round(CONTENT_WIDTH * 0.55) }),
        cell([
          labelValue("INVOICE NO.", invoiceNo, true),
          labelValue("DATE", invoiceDate),
        ], { width: CONTENT_WIDTH - Math.round(CONTENT_WIDTH * 0.55) }),
      ],
    })],
  });

  const colNo = 700;
  const colAmt = 1900;
  const colDesc = CONTENT_WIDTH - colNo - colAmt;
  const thinBorders = {
    top: { style: BorderStyle.SINGLE, size: 2, color: "D7DCE3" },
    bottom: { style: BorderStyle.SINGLE, size: 2, color: "D7DCE3" },
    left: { style: BorderStyle.SINGLE, size: 2, color: "D7DCE3" },
    right: { style: BorderStyle.SINGLE, size: 2, color: "D7DCE3" },
    insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: "D7DCE3" },
    insideVertical: { style: BorderStyle.SINGLE, size: 2, color: "D7DCE3" },
  };

  const headerRow = new TableRow({
    tableHeader: true,
    children: [
      cell([new Paragraph({ children: [new TextRun({ text: "NO.", bold: true, color: "FFFFFF", size: 18 })] })], { width: colNo, shading: BRAND_DARK, borders: thinBorders }),
      cell([new Paragraph({ children: [new TextRun({ text: "DESCRIPTION", bold: true, color: "FFFFFF", size: 18 })] })], { width: colDesc, shading: BRAND_DARK, borders: thinBorders }),
      cell([new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "AMOUNT", bold: true, color: "FFFFFF", size: 18 })] })], { width: colAmt, shading: BRAND_DARK, borders: thinBorders }),
    ],
  });

  const itemRows = items.map((it, idx) => new TableRow({
    children: [
      cell([new Paragraph({ children: [new TextRun({ text: String(idx + 1), size: 20 })] })], { width: colNo, borders: thinBorders, shading: idx % 2 === 1 ? LIGHT_FILL : undefined }),
      cell(
        it.description.split("\n").map((l) => new Paragraph({ spacing: { after: 20 }, children: [new TextRun({ text: l, size: 20, font: CJK_FONT })] })),
        { width: colDesc, borders: thinBorders, shading: idx % 2 === 1 ? LIGHT_FILL : undefined },
      ),
      cell([new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: it.amount, size: 20 })] })], { width: colAmt, borders: thinBorders, shading: idx % 2 === 1 ? LIGHT_FILL : undefined }),
    ],
  }));

  const totalRow = new TableRow({
    children: [
      cell([new Paragraph({ children: [] })], { width: colNo, borders: thinBorders }),
      cell([new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "TOTAL", bold: true, size: 20, color: BRAND_DARK })] })], { width: colDesc, borders: thinBorders, shading: LIGHT_FILL }),
      cell([new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: total, bold: true, size: 22, color: BRAND_DARK })] })], { width: colAmt, borders: thinBorders, shading: LIGHT_FILL }),
    ],
  });

  const itemsTable = new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: [colNo, colDesc, colAmt],
    rows: [headerRow, ...itemRows, totalRow],
  });

  const paymentSection = [
    new Paragraph({ spacing: { before: 400, after: 100 }, children: [new TextRun({ text: "PAYMENT DETAILS", bold: true, size: 18, color: GREY })] }),
    new Paragraph({ spacing: { after: 20 }, children: [new TextRun({ text: "Dreambiggg Co. Ltd.", size: 20 })] }),
    new Paragraph({ spacing: { after: 20 }, children: [new TextRun({ text: "HSBC", size: 20 })] }),
    new Paragraph({ children: [new TextRun({ text: "Account No. 652-298985-838", size: 20 })] }),
  ];

  const termsSection = termsUrl ? [
    new Paragraph({ spacing: { before: 300, after: 80 }, children: [new TextRun({ text: "TERMS & CONDITIONS", bold: true, size: 18, color: GREY })] }),
    new Paragraph({ children: [new TextRun({ text: termsUrl, size: 18, color: BRAND_BLUE })] }),
  ] : [];

  const footer = [
    new Paragraph({
      spacing: { before: 500 },
      alignment: AlignmentType.CENTER,
      border: { top: { style: BorderStyle.SINGLE, size: 4, color: "D7DCE3", space: 12 } },
      children: [new TextRun({ text: "Thank you for your business.", italics: true, size: 18, color: GREY })],
    }),
  ];

  const doc = new Document({
    sections: [{
      properties: {
        page: {
          size: { width: PAGE_WIDTH_DXA, height: 16839 },
          margin: { top: MARGIN_DXA, bottom: MARGIN_DXA, left: MARGIN_DXA, right: MARGIN_DXA },
        },
      },
      children: [headerTable, ruleParagraph, metaTable, new Paragraph({ spacing: { before: 300, after: 150 }, children: [] }), itemsTable, ...paymentSection, ...termsSection, ...footer],
    }],
  });

  return Packer.toBuffer(doc).then((buf) => {
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, buf);
    return outPath;
  });
}

module.exports = { buildInvoice };
