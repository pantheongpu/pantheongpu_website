// Minimal XLSX writer: enough of the format to emit a workbook, and nothing
// more.
//
// An .xlsx file is a ZIP of XML parts. Writing those directly costs about
// two hundred lines; the usual library for it is ~900 KB, which is more than
// this whole site's JavaScript put together and would be downloaded by
// everyone to serve the few who click Export. So this builds the archive
// itself, and is loaded only when an export is actually requested.
//
// Deliberately not supported: styles, formulas, merged cells, shared
// strings. The benchmark export is a grid of numbers and short strings, and
// every feature left out is one that cannot go wrong in a spreadsheet
// someone opens six months from now.

(function (global) {
    "use strict";

    const CRC_TABLE = (() => {
        const table = new Uint32Array(256);
        for (let i = 0; i < 256; i++) {
            let c = i;
            for (let k = 0; k < 8; k++) {
                c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
            }
            table[i] = c >>> 0;
        }
        return table;
    })();

    function crc32(bytes) {
        let crc = 0xFFFFFFFF;
        for (let i = 0; i < bytes.length; i++) {
            crc = CRC_TABLE[(crc ^ bytes[i]) & 0xFF] ^ (crc >>> 8);
        }
        return (crc ^ 0xFFFFFFFF) >>> 0;
    }

    const utf8 = new TextEncoder();

    // XML 1.0 forbids most control characters outright -- they cannot be
    // escaped, only removed. A single stray one makes the whole workbook
    // unopenable rather than showing a bad cell, so they are stripped here
    // and not at the call site.
    function escapeXml(value) {
        return String(value)
            .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&apos;");
    }

    // 1 -> A, 26 -> Z, 27 -> AA. The counter export runs to ~190 columns, so
    // single-letter references are not enough and a wrong one here silently
    // shifts a whole sheet sideways.
    function columnRef(index) {
        let ref = "";
        let n = index;
        while (n > 0) {
            const remainder = (n - 1) % 26;
            ref = String.fromCharCode(65 + remainder) + ref;
            n = Math.floor((n - remainder) / 26);
        }
        return ref;
    }

    function cellXml(cell, rowNumber, columnIndex) {
        const ref = `${columnRef(columnIndex)}${rowNumber}`;
        if (cell === null || cell === undefined || cell === "") {
            // An empty cell, not the text "N/A". A spreadsheet reads a blank
            // as "not measured" and still averages the column around it;
            // "N/A" turns the column into text and breaks every formula.
            return `<c r="${ref}"/>`;
        }
        if (typeof cell === "number" && Number.isFinite(cell)) {
            return `<c r="${ref}"><v>${cell}</v></c>`;
        }
        // Inline strings, so there is no shared-string table to keep in sync.
        return `<c r="${ref}" t="inlineStr"><is><t xml:space="preserve">`
            + escapeXml(cell) + `</t></is></c>`;
    }

    function sheetXml(rows) {
        const body = rows.map((row, rowIndex) => {
            const number = rowIndex + 1;
            const cells = row.map((cell, columnIndex) =>
                cellXml(cell, number, columnIndex + 1)).join("");
            return `<row r="${number}">${cells}</row>`;
        }).join("");
        return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>`
            + `<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">`
            + `<sheetData>${body}</sheetData></worksheet>`;
    }

    function workbookParts(sheets) {
        const overrides = sheets.map((sheet, i) =>
            `<Override PartName="/xl/worksheets/sheet${i + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>`
        ).join("");
        const sheetTags = sheets.map((sheet, i) =>
            `<sheet name="${escapeXml(sheet.name)}" sheetId="${i + 1}" r:id="rId${i + 1}"/>`
        ).join("");
        const relTags = sheets.map((sheet, i) =>
            `<Relationship Id="rId${i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet${i + 1}.xml"/>`
        ).join("");

        const parts = [
            ["[Content_Types].xml",
                `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>`
                + `<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">`
                + `<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>`
                + `<Default Extension="xml" ContentType="application/xml"/>`
                + `<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>`
                + overrides + `</Types>`],
            ["_rels/.rels",
                `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>`
                + `<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">`
                + `<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>`
                + `</Relationships>`],
            ["xl/workbook.xml",
                `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>`
                + `<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" `
                + `xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">`
                + `<sheets>${sheetTags}</sheets></workbook>`],
            ["xl/_rels/workbook.xml.rels",
                `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>`
                + `<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">`
                + relTags + `</Relationships>`],
        ];
        sheets.forEach((sheet, i) => {
            parts.push([`xl/worksheets/sheet${i + 1}.xml`, sheetXml(sheet.rows)]);
        });
        return parts;
    }

    async function deflate(bytes) {
        // deflate-raw is what ZIP method 8 stores. Where it is unavailable the
        // entry is stored uncompressed instead -- a bigger file, still a valid
        // workbook, which is the right way round for a fallback.
        if (typeof global.CompressionStream !== "function") return null;
        try {
            const stream = new global.CompressionStream("deflate-raw");
            const compressed = new Response(
                new Blob([bytes]).stream().pipeThrough(stream)
            );
            return new Uint8Array(await compressed.arrayBuffer());
        } catch (err) {
            return null;
        }
    }

    function u16(value) { return [value & 0xFF, (value >>> 8) & 0xFF]; }
    function u32(value) {
        return [value & 0xFF, (value >>> 8) & 0xFF,
                (value >>> 16) & 0xFF, (value >>> 24) & 0xFF];
    }

    async function buildWorkbook(sheets) {
        const chunks = [];
        const directory = [];
        let offset = 0;

        for (const [name, xml] of workbookParts(sheets)) {
            const raw = utf8.encode(xml);
            const packed = await deflate(raw);
            const body = packed || raw;
            const method = packed ? 8 : 0;
            const crc = crc32(raw);
            const nameBytes = utf8.encode(name);

            const header = [
                ...u32(0x04034B50), ...u16(20), ...u16(0), ...u16(method),
                ...u16(0), ...u16(0),               // fixed DOS time/date
                ...u32(crc), ...u32(body.length), ...u32(raw.length),
                ...u16(nameBytes.length), ...u16(0),
            ];
            chunks.push(new Uint8Array(header), nameBytes, body);

            directory.push({ nameBytes, method, crc, offset,
                             packedSize: body.length, rawSize: raw.length });
            offset += header.length + nameBytes.length + body.length;
        }

        const centralStart = offset;
        let centralSize = 0;
        for (const entry of directory) {
            const record = [
                ...u32(0x02014B50), ...u16(20), ...u16(20), ...u16(0),
                ...u16(entry.method), ...u16(0), ...u16(0),
                ...u32(entry.crc), ...u32(entry.packedSize), ...u32(entry.rawSize),
                ...u16(entry.nameBytes.length), ...u16(0), ...u16(0),
                ...u16(0), ...u16(0), ...u32(0), ...u32(entry.offset),
            ];
            chunks.push(new Uint8Array(record), entry.nameBytes);
            centralSize += record.length + entry.nameBytes.length;
        }

        chunks.push(new Uint8Array([
            ...u32(0x06054B50), ...u16(0), ...u16(0),
            ...u16(directory.length), ...u16(directory.length),
            ...u32(centralSize), ...u32(centralStart), ...u16(0),
        ]));

        return new Blob(chunks, {
            type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        });
    }

    global.PantheonXLSX = { buildWorkbook, columnRef, escapeXml, crc32 };
})(window);
