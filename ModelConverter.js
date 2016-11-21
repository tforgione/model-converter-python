const fs = require('fs');

class Vertex {
    constructor(x,y,z) {
        this.x = x;
        this.y = y;
        this.z = z;
    }

    fromArray(arr) {
        this.x = arr[0];
        this.y = arr[1];
        this.z = arr[2];
        return this;
    }
}
const Normal = Vertex;
const TexCoord = Vertex;

class Face {
    constructor(a,b,c,aTex,bTex,cTex,aNorm,bNorm,cNorm,mtl) {
        this.a = a;
        this.b = b;
        this.c = c;

        this.aTex = aTex;
        this.bTex = bTex;
        this.cTex = cTex;

        this.aNorm = aNorm;
        this.bNorm = bNorm;
        this.cNorm = cNorm;

        this.mtl = mtl;
    }

    fromArray(arr) {
        this.a     = arr[0];
        this.aTex  = arr[1];
        this.aNorm = arr[2];

        this.b     = arr[3];
        this.bTex  = arr[4];
        this.bNorm = arr[5];

        this.c     = arr[6];
        this.cTex  = arr[7];
        this.cNorm = arr[8];
                           ;
        this.mtl   = arr[9];
        return this;
    }
}


class ModelParser {

    constructor() {
        if (this.constructor === ModelParser) {
            throw new Error("Can't instanciate abstract class ModelParser");
        }
        this.vertices = [];
        this.normals = [];
        this.texCoords = [];
        this.faces = [];
    }

    addVertex(vertex) {
        this.vertices.push(vertex);
    }

    addTexCoord(texCoord) {
        this.texCoords.push(texCoord);
    }

    addNormal(normal) {
        this.normals.push(normal);
    }

    addFace(face) {
        this.faces.push(face);
    }

    parseLine(string) {
        if (this.constructor === ModelParser) {
            throw new Error("Can't call abstract method ModelParser.parseLine");
        }
    }

    parseFile(path) {
        fs
            .readFileSync(path, 'utf-8')
            .split('\n')
            // .map((l) => l.slice(0,-1))
            .map((a) => this.parseLine(a));
    }

}

class OBJParser extends ModelParser {

    constructor() {
        super();
        this.materials = [];
    }

    parseLine(string) {
        let split = string.split(' ');

        switch (split.shift()) {
            case 'usemtl': this.currentMaterial = split[0]; break;

            case 'v':  this.addVertex  (new Vertex().  fromArray(split)); break;
            case 'vn': this.addNormal  (new Normal().  fromArray(split)); break;
            case 'vt': this.addTexCoord(new TexCoord().fromArray(split)); break;
            case 'f':  this.addFace    (new Face()    .fromArray(split.map(s => s.split('/')).reduce((a,b) => a.concat(b), [])));

        }
    }

}

class Exporter {
    constructor(model) {
        this.model = model;
    }
}

class OBJExporter extends Exporter {
    constructor(model) {
        super(model);
    }

    toString() {
        let string = "";

        for (let vertex of this.model.vertices) {
            string += "n " + [vertex.x, vertex.y, vertex.z].join(' ') + "\n";
        }

        string += "\n";

        for (let texCoord of this.model.texCoords) {
            string += "vt " + [texCoord.x, texCoord.y].join(' ') + "\n";
        }

        string += "\n"

        for (let normal of this.model.normals) {
            string += "vn " + [normal.x, normal.y, normal.z].join(' ') + "\n";
        }

        string += "\n";

        for (let face of this.model.faces) {
            string += "f ";
            string += ['a', 'b', 'c'].map(a => [face[a], face[a + 'Tex'], face[a + 'Norm']].join('/')).join(' ');
            string += '\n';
        }

        return string;
    }
}

if (require.main === module) {

    let parser = new OBJParser();
    parser.parseFile('./examples/cube.obj');

    let exporter = new OBJExporter(parser);
    let string = exporter.toString();

    console.log(string);

}
