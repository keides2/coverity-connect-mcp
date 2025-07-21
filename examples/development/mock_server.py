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

# ダミーユーザーデータ
DUMMY_USERS = [
    {
        "name": "admin",
        "email": "admin@company.com",
        "familyName": "Administrator", 
        "givenName": "System",
        "disabled": False,
        "locked": False,
        "superUser": True,
        "groupNames": ["Administrators", "Users"],
        "roleAssignments": [
            {
                "roleName": "administrator",
                "scope": "global",
                "username": "admin",
                "roleAssignmentType": "user"
            }
        ],
        "lastLogin": "2024-07-21T10:00:00Z",
        "dateCreated": "2024-01-01T00:00:00Z",
        "dateModified": "2024-07-21T10:00:00Z",
        "local": True,
        "locale": "ja_JP"
    },
    {
        "name": "developer1",
        "email": "dev1@company.com",
        "familyName": "開発",
        "givenName": "太郎",
        "disabled": False,
        "locked": False,
        "superUser": False,
        "groupNames": ["Users"],
        "roleAssignments": [
            {
                "roleName": "developer",
                "scope": "global", 
                "username": "developer1",
                "roleAssignmentType": "user"
            }
        ],
        "lastLogin": "2024-07-20T15:30:00Z",
        "dateCreated": "2024-02-01T00:00:00Z",
        "dateModified": "2024-07-20T15:30:00Z",
        "local": True,
        "locale": "ja_JP"
    },
    {
        "name": "projectowner1",
        "email": "owner1@company.com",
        "familyName": "プロジェクト",
        "givenName": "花子",
        "disabled": False,
        "locked": False,
        "superUser": False,
        "groupNames": ["Users"],
        "roleAssignments": [
            {
                "roleName": "projectOwner",
                "scope": "project",
                "username": "projectowner1",
                "roleAssignmentType": "user"
            }
        ],
        "lastLogin": "2024-07-19T09:15:00Z",
        "dateCreated": "2024-03-01T00:00:00Z",
        "dateModified": "2024-07-19T09:15:00Z",
        "local": True,
        "locale": "ja_JP"
    },
    {
        "name": "analyst1",
        "email": "analyst1@company.com",
        "familyName": "分析",
        "givenName": "次郎",
        "disabled": False,
        "locked": False,
        "superUser": False,
        "groupNames": ["Users"],
        "roleAssignments": [
            {
                "roleName": "analyst",
                "scope": "global",
                "username": "analyst1",
                "roleAssignmentType": "user"
            }
        ],
        "lastLogin": "2024-07-18T13:45:00Z",
        "dateCreated": "2024-04-01T00:00:00Z",
        "dateModified": "2024-07-18T13:45:00Z",
        "local": True,
        "locale": "en_US"
    },
    {
        "name": "disabled_user",
        "email": "disabled@company.com",
        "familyName": "無効",
        "givenName": "ユーザー",
        "disabled": True,
        "locked": False,
        "superUser": False,
        "groupNames": ["Users"],
        "roleAssignments": [
            {
                "roleName": "viewer",
                "scope": "global",
                "username": "disabled_user",
                "roleAssignmentType": "user"
            }
        ],
        "lastLogin": "2024-05-01T10:00:00Z",
        "dateCreated": "2024-05-01T00:00:00Z",
        "dateModified": "2024-06-01T00:00:00Z",
        "local": True,
        "locale": "ja_JP"
    }
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

# ==================== ユーザー管理 REST API エンドポイント ====================

@app.route('/api/v2/users', methods=['GET'])
def get_users():
    """ユーザー一覧取得 API"""
    try:
        # パラメータ取得
        disabled = request.args.get('disabled', 'false').lower() == 'true'
        include_details = request.args.get('includeDetails', 'true').lower() == 'true'
        locked = request.args.get('locked', 'false').lower() == 'true'
        row_count = int(request.args.get('rowCount', '200'))
        offset = int(request.args.get('offset', '0'))
        sort_column = request.args.get('sortColumn', 'name')
        sort_order = request.args.get('sortOrder', 'asc')
        
        # フィルタリング
        filtered_users = []
        for user in DUMMY_USERS:
            # disabled フィルタ
            if not disabled and user.get('disabled', False):
                continue
            # locked フィルタ  
            if not locked and user.get('locked', False):
                continue
            
            filtered_users.append(user)
        
        # ソート
        reverse_sort = sort_order.lower() == 'desc'
        if sort_column == 'name':
            filtered_users.sort(key=lambda x: x.get('name', ''), reverse=reverse_sort)
        elif sort_column == 'email':
            filtered_users.sort(key=lambda x: x.get('email', ''), reverse=reverse_sort)
        elif sort_column == 'dateCreated':
            filtered_users.sort(key=lambda x: x.get('dateCreated', ''), reverse=reverse_sort)
        
        # ページング
        total_count = len(filtered_users)
        start_idx = offset
        end_idx = min(offset + row_count, total_count)
        paged_users = filtered_users[start_idx:end_idx]
        
        response_data = {
            "users": paged_users,
            "totalCount": total_count,
            "offset": offset,
            "rowCount": len(paged_users)
        }
        
        return Response(
            json.dumps(response_data, indent=2, ensure_ascii=False),
            mimetype='application/json'
        )
        
    except Exception as e:
        error_response = {
            "error": f"ユーザー一覧取得エラー: {str(e)}",
            "httpStatusCode": 500
        }
        return Response(
            json.dumps(error_response, ensure_ascii=False),
            mimetype='application/json',
            status=500
        )

@app.route('/api/v2/users/<username>', methods=['GET'])
def get_user_details(username):
    """特定ユーザー詳細取得 API"""
    try:
        # ユーザー検索
        found_user = None
        for user in DUMMY_USERS:
            if user.get('name') == username:
                found_user = user
                break
        
        if not found_user:
            error_response = {
                "statusMessage": "見つかりません",
                "httpStatusCode": 404,
                "detailMessage": f"{username} に一致するユーザーが見つかりません。"
            }
            return Response(
                json.dumps(error_response, ensure_ascii=False),
                mimetype='application/json',
                status=404
            )
        
        response_data = {
            "users": [found_user]
        }
        
        return Response(
            json.dumps(response_data, indent=2, ensure_ascii=False),
            mimetype='application/json'
        )
        
    except Exception as e:
        error_response = {
            "error": f"ユーザー詳細取得エラー: {str(e)}",
            "httpStatusCode": 500
        }
        return Response(
            json.dumps(error_response, ensure_ascii=False),
            mimetype='application/json',
            status=500
        )

@app.route('/api/v2/users/summary', methods=['GET'])
def get_users_summary():
    """ユーザーサマリー情報取得 API"""
    try:
        total_users = len(DUMMY_USERS)
        active_users = len([u for u in DUMMY_USERS if not u.get('disabled', False)])
        disabled_users = total_users - active_users
        admin_users = len([u for u in DUMMY_USERS if u.get('superUser', False)])
        
        # ロール別集計
        role_counts = {}
        for user in DUMMY_USERS:
            for role_assignment in user.get('roleAssignments', []):
                role_name = role_assignment.get('roleName', 'unknown')
                role_counts[role_name] = role_counts.get(role_name, 0) + 1
        
        response_data = {
            "summary": {
                "totalUsers": total_users,
                "activeUsers": active_users,
                "disabledUsers": disabled_users,
                "adminUsers": admin_users,
                "roleDistribution": role_counts
            },
            "lastUpdated": "2024-07-21T10:00:00Z"
        }
        
        return Response(
            json.dumps(response_data, indent=2, ensure_ascii=False),
            mimetype='application/json'
        )
        
    except Exception as e:
        error_response = {
            "error": f"ユーザーサマリー取得エラー: {str(e)}",
            "httpStatusCode": 500
        }
        return Response(
            json.dumps(error_response, ensure_ascii=False),
            mimetype='application/json',
            status=500
        )

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
    print("� Available test users:")
    print("   - admin (administrator)")
    print("   - developer1 (developer)")
    print("   - projectowner1 (project owner)")
    print("   - analyst1 (analyst)")
    print("   - disabled_user (disabled)")
    print("")
    print("🔗 User API endpoints:")
    print("   GET /api/v2/users - List all users")
    print("   GET /api/v2/users/{username} - Get user details")
    print("   GET /api/v2/users/summary - Get user summary")
    print("")
    print("�🚀 Starting Flask server...")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
