#!/usr/bin/env python3
"""
ダミー Coverity Connect サーバー
テスト用のSOAP APIモックサーバー
"""

from flask import Flask, request, Response
import xml.etree.ElementTree as ET
from datetime import datetime
import json

app = Flask(__name__)

# ダミーデータ
DUMMY_PROJECTS = [
    {
        "projectKey": "PROJ001",
        "name": "WebApplication",
        "dateCreated": "2024-01-15T10:30:00Z",
        "userCreated": "developer1"
    },
    {
        "projectKey": "PROJ002", 
        "name": "MobileApp",
        "dateCreated": "2024-02-20T14:45:00Z",
        "userCreated": "developer2"
    },
    {
        "projectKey": "PROJ003",
        "name": "APIService", 
        "dateCreated": "2024-03-10T09:15:00Z",
        "userCreated": "developer3"
    }
]

DUMMY_STREAMS = {
    "WebApplication": [
        {"name": "main", "description": "Main development branch"},
        {"name": "develop", "description": "Development branch"},
        {"name": "release", "description": "Release preparation"}
    ],
    "MobileApp": [
        {"name": "main", "description": "Main branch"},
        {"name": "feature", "description": "Feature development"}
    ],
    "APIService": [
        {"name": "main", "description": "Production branch"}
    ]
}

DUMMY_SNAPSHOTS = [
    {"id": "12345", "dateCreated": "2024-07-15T10:00:00Z", "user": "jenkins"},
    {"id": "12346", "dateCreated": "2024-07-14T15:30:00Z", "user": "developer1"},
    {"id": "12347", "dateCreated": "2024-07-13T11:20:00Z", "user": "developer2"}
]

def create_soap_response(content):
    """SOAP レスポンス形式を作成"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        {content}
    </soap:Body>
</soap:Envelope>"""

@app.route('/ws/v9/configurationservice', methods=['GET'])
def configuration_service_wsdl():
    """Configuration Service WSDL"""
    wsdl_content = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://schemas.xmlsoap.org/wsdl/"
             xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
             xmlns:tns="http://ws.coverity.com/v9"
             targetNamespace="http://ws.coverity.com/v9">
    
    <types>
        <schema xmlns="http://www.w3.org/2001/XMLSchema" targetNamespace="http://ws.coverity.com/v9">
            <!-- Simplified schema for testing -->
        </schema>
    </types>
    
    <message name="getProjectsRequest">
        <part name="filterSpec" type="tns:projectFilterSpecDataObj"/>
    </message>
    
    <message name="getProjectsResponse">
        <part name="return" type="tns:projectDataObj"/>
    </message>
    
    <portType name="ConfigurationServicePortType">
        <operation name="getProjects">
            <input message="tns:getProjectsRequest"/>
            <output message="tns:getProjectsResponse"/>
        </operation>
    </portType>
    
    <binding name="ConfigurationServiceBinding" type="tns:ConfigurationServicePortType">
        <soap:binding transport="http://schemas.xmlsoap.org/soap/http"/>
        <operation name="getProjects">
            <soap:operation soapAction="getProjects"/>
            <input><soap:body use="literal"/></input>
            <o><soap:body use="literal"/></o>
        </operation>
    </binding>
    
    <service name="ConfigurationService">
        <port name="ConfigurationServicePort" binding="tns:ConfigurationServiceBinding">
            <soap:address location="http://localhost:5000/ws/v9/configurationservice"/>
        </port>
    </service>
</definitions>"""
    
    return Response(wsdl_content, mimetype='text/xml')

@app.route('/ws/v9/configurationservice', methods=['POST'])
def configuration_service_soap():
    """Configuration Service SOAP エンドポイント"""
    try:
        # SOAPリクエストを解析
        soap_action = request.headers.get('SOAPAction', '').strip('"')
        request_data = request.data.decode('utf-8', errors='ignore')
        
        print(f"📨 SOAP Request: {soap_action}")
        print(f"📄 Request Data: {request_data[:200]}...")
        
        if 'getProjects' in soap_action or 'getProjects' in request_data:
            # プロジェクト一覧を返す
            projects_xml = ""
            for proj in DUMMY_PROJECTS:
                projects_xml += f"""
                <ns1:projectDataObj>
                    <ns1:projectKey>{proj['projectKey']}</ns1:projectKey>
                    <ns1:id>
                        <ns1:name>{proj['name']}</ns1:name>
                    </ns1:id>
                    <ns1:dateCreated>{proj['dateCreated']}</ns1:dateCreated>
                    <ns1:userCreated>{proj['userCreated']}</ns1:userCreated>
                </ns1:projectDataObj>"""
            
            response_content = f"""
            <ns1:getProjectsResponse xmlns:ns1="http://ws.coverity.com/v9">
                {projects_xml}
            </ns1:getProjectsResponse>"""
            
            print("✅ Returning projects list")
            return Response(create_soap_response(response_content), mimetype='text/xml')
        
        elif 'getSnapshotsForStream' in request_data:
            # スナップショット一覧を返す
            snapshots_xml = ""
            for snap in DUMMY_SNAPSHOTS:
                snapshots_xml += f"""
                <ns1:snapshotDataObj>
                    <ns1:id>{snap['id']}</ns1:id>
                    <ns1:dateCreated>{snap['dateCreated']}</ns1:dateCreated>
                    <ns1:user>{snap['user']}</ns1:user>
                </ns1:snapshotDataObj>"""
            
            response_content = f"""
            <ns1:getSnapshotsForStreamResponse xmlns:ns1="http://ws.coverity.com/v9">
                {snapshots_xml}
            </ns1:getSnapshotsForStreamResponse>"""
            
            print("✅ Returning snapshots list")
            return Response(create_soap_response(response_content), mimetype='text/xml')
        
        else:
            # 汎用的な成功レスポンス
            response_content = """
            <ns1:genericResponse xmlns:ns1="http://ws.coverity.com/v9">
                <ns1:status>SUCCESS</ns1:status>
                <ns1:message>Mock response from dummy server</ns1:message>
            </ns1:genericResponse>"""
            
            print("✅ Returning generic success response")
            return Response(create_soap_response(response_content), mimetype='text/xml')
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        # エラーレスポンス
        error_content = f"""
        <soap:Fault>
            <faultcode>Server</faultcode>
            <faultstring>Dummy server error: {str(e)}</faultstring>
        </soap:Fault>"""
        
        return Response(create_soap_response(error_content), mimetype='text/xml', status=500)

@app.route('/ws/v9/defectservice', methods=['GET'])
def defect_service_wsdl():
    """Defect Service WSDL (修正版)"""
    wsdl_content = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://schemas.xmlsoap.org/wsdl/"
             xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
             xmlns:tns="http://ws.coverity.com/v9"
             targetNamespace="http://ws.coverity.com/v9">
    
    <types>
        <schema xmlns="http://www.w3.org/2001/XMLSchema" targetNamespace="http://ws.coverity.com/v9">
            <!-- Simplified schema for testing -->
        </schema>
    </types>
    
    <message name="getMergedDefectsRequest">
        <part name="filterSpec" type="tns:defectFilterSpecDataObj"/>
    </message>
    
    <message name="getMergedDefectsResponse">
        <part name="return" type="tns:mergedDefectDataObj"/>
    </message>
    
    <portType name="DefectServicePortType">
        <operation name="getMergedDefectsForSnapshotScope">
            <input message="tns:getMergedDefectsRequest"/>
            <output message="tns:getMergedDefectsResponse"/>
        </operation>
    </portType>
    
    <binding name="DefectServiceBinding" type="tns:DefectServicePortType">
        <soap:binding transport="http://schemas.xmlsoap.org/soap/http"/>
        <operation name="getMergedDefectsForSnapshotScope">
            <soap:operation soapAction="getMergedDefectsForSnapshotScope"/>
            <input><soap:body use="literal"/></input>
            <o><soap:body use="literal"/></o>
        </operation>
    </binding>
    
    <service name="DefectService">
        <port name="DefectServicePort" binding="tns:DefectServiceBinding">
            <soap:address location="http://localhost:5000/ws/v9/defectservice"/>
        </port>
    </service>
</definitions>"""
    
    return Response(wsdl_content, mimetype='text/xml')

@app.route('/ws/v9/defectservice', methods=['POST'])
def defect_service_soap():
    """Defect Service SOAP エンドポイント"""
    print("📨 Defect Service Request received")
    
    # ダミーの欠陥データを返す
    defects_xml = """
    <ns1:getMergedDefectsForSnapshotScopeResponse xmlns:ns1="http://ws.coverity.com/v9">
        <ns1:totalNumberOfRecords>3</ns1:totalNumberOfRecords>
        <ns1:mergedDefectIds>
            <ns1:cid>1001</ns1:cid>
        </ns1:mergedDefectIds>
        <ns1:mergedDefectIds>
            <ns1:cid>1002</ns1:cid>
        </ns1:mergedDefectIds>
        <ns1:mergedDefectIds>
            <ns1:cid>1003</ns1:cid>
        </ns1:mergedDefectIds>
    </ns1:getMergedDefectsForSnapshotScopeResponse>"""
    
    print("✅ Returning defects list")
    return Response(create_soap_response(defects_xml), mimetype='text/xml')

@app.route('/status', methods=['GET'])
def status():
    """サーバーステータス確認"""
    return {
        "status": "running",
        "message": "Dummy Coverity Connect Server",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/ws/v9/configurationservice",
            "/ws/v9/defectservice"
        ],
        "dummy_data": {
            "projects": len(DUMMY_PROJECTS),
            "streams": sum(len(streams) for streams in DUMMY_STREAMS.values()),
            "snapshots": len(DUMMY_SNAPSHOTS)
        }
    }

@app.route('/', methods=['GET'])
def root():
    """ルートページ"""
    return f"""
    <h1>🎭 Dummy Coverity Connect Server</h1>
    <p>テスト用のモックサーバーが動作中です。</p>
    <h2>📋 利用可能なエンドポイント</h2>
    <ul>
        <li><a href="/status">📊 Status</a></li>
        <li><a href="/ws/v9/configurationservice?wsdl">📄 Configuration Service WSDL</a></li>
        <li><a href="/ws/v9/defectservice?wsdl">📄 Defect Service WSDL</a></li>
    </ul>
    
    <h2>🔧 MCP Server設定</h2>
    <pre>
COVERITY_HOST=localhost
COVERITY_PORT=5000
COVERITY_SSL=False
COVAUTHUSER=dummy_user
COVAUTHKEY=dummy_key
    </pre>
    
    <h2>📊 ダミーデータ</h2>
    <ul>
        <li>プロジェクト: {len(DUMMY_PROJECTS)}個</li>
        <li>ストリーム: {sum(len(streams) for streams in DUMMY_STREAMS.values())}個</li>
        <li>スナップショット: {len(DUMMY_SNAPSHOTS)}個</li>
    </ul>
    
    <p><strong>このサーバーはCoverity Connect MCP Serverのテスト用です。</strong></p>
    """

if __name__ == '__main__':
    print("🎭 Starting Dummy Coverity Connect Server...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🔧 Configure your MCP server with:")
    print("   COVERITY_HOST=localhost")
    print("   COVERITY_PORT=5000") 
    print("   COVERITY_SSL=False")
    print("   COVAUTHUSER=dummy_user")
    print("   COVAUTHKEY=dummy_key")
    print("")
    print("🚀 Starting Flask server...")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
