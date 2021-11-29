# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: requests.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import common_pb2 as common__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0erequests.proto\x1a\x0c\x63ommon.proto\"(\n\x0f\x43\x61talogsRequest\x12\x15\n\rconnection_id\x18\x01 \x01(\t\"0\n\x17\x44\x61tabasePropertyRequest\x12\x15\n\rconnection_id\x18\x01 \x01(\t\"P\n\x0eSchemasRequest\x12\x0f\n\x07\x63\x61talog\x18\x01 \x01(\t\x12\x16\n\x0eschema_pattern\x18\x02 \x01(\t\x12\x15\n\rconnection_id\x18\x03 \x01(\t\"\x95\x01\n\rTablesRequest\x12\x0f\n\x07\x63\x61talog\x18\x01 \x01(\t\x12\x16\n\x0eschema_pattern\x18\x02 \x01(\t\x12\x1a\n\x12table_name_pattern\x18\x03 \x01(\t\x12\x11\n\ttype_list\x18\x04 \x03(\t\x12\x15\n\rhas_type_list\x18\x06 \x01(\x08\x12\x15\n\rconnection_id\x18\x07 \x01(\t\"*\n\x11TableTypesRequest\x12\x15\n\rconnection_id\x18\x01 \x01(\t\"\x89\x01\n\x0e\x43olumnsRequest\x12\x0f\n\x07\x63\x61talog\x18\x01 \x01(\t\x12\x16\n\x0eschema_pattern\x18\x02 \x01(\t\x12\x1a\n\x12table_name_pattern\x18\x03 \x01(\t\x12\x1b\n\x13\x63olumn_name_pattern\x18\x04 \x01(\t\x12\x15\n\rconnection_id\x18\x05 \x01(\t\"(\n\x0fTypeInfoRequest\x12\x15\n\rconnection_id\x18\x01 \x01(\t\"`\n\x12PrimaryKeysRequest\x12\x0f\n\x07\x63\x61talog\x18\x01 \x01(\t\x12\x0e\n\x06schema\x18\x02 \x01(\t\x12\x12\n\ntable_name\x18\x03 \x01(\t\x12\x15\n\rconnection_id\x18\x04 \x01(\t\"a\n\x13ImportedKeysRequest\x12\x0f\n\x07\x63\x61talog\x18\x01 \x01(\t\x12\x0e\n\x06schema\x18\x02 \x01(\t\x12\x12\n\ntable_name\x18\x03 \x01(\t\x12\x15\n\rconnection_id\x18\x04 \x01(\t\"a\n\x13\x45xportedKeysRequest\x12\x0f\n\x07\x63\x61talog\x18\x01 \x01(\t\x12\x0e\n\x06schema\x18\x02 \x01(\t\x12\x12\n\ntable_name\x18\x03 \x01(\t\x12\x15\n\rconnection_id\x18\x04 \x01(\t\"\x83\x01\n\x10IndexInfoRequest\x12\x0f\n\x07\x63\x61talog\x18\x01 \x01(\t\x12\x0e\n\x06schema\x18\x02 \x01(\t\x12\x12\n\ntable_name\x18\x03 \x01(\t\x12\x0e\n\x06unique\x18\x04 \x01(\x08\x12\x13\n\x0b\x61pproximate\x18\x05 \x01(\x08\x12\x15\n\rconnection_id\x18\x06 \x01(\t\"\xa1\x01\n\x18PrepareAndExecuteRequest\x12\x15\n\rconnection_id\x18\x01 \x01(\t\x12\x0b\n\x03sql\x18\x02 \x01(\t\x12\x15\n\rmax_row_count\x18\x03 \x01(\x04\x12\x14\n\x0cstatement_id\x18\x04 \x01(\r\x12\x16\n\x0emax_rows_total\x18\x05 \x01(\x03\x12\x1c\n\x14\x66irst_frame_max_size\x18\x06 \x01(\x05\"c\n\x0ePrepareRequest\x12\x15\n\rconnection_id\x18\x01 \x01(\t\x12\x0b\n\x03sql\x18\x02 \x01(\t\x12\x15\n\rmax_row_count\x18\x03 \x01(\x04\x12\x16\n\x0emax_rows_total\x18\x04 \x01(\x03\"\x80\x01\n\x0c\x46\x65tchRequest\x12\x15\n\rconnection_id\x18\x01 \x01(\t\x12\x14\n\x0cstatement_id\x18\x02 \x01(\r\x12\x0e\n\x06offset\x18\x03 \x01(\x04\x12\x1b\n\x13\x66\x65tch_max_row_count\x18\x04 \x01(\r\x12\x16\n\x0e\x66rame_max_size\x18\x05 \x01(\x05\"/\n\x16\x43reateStatementRequest\x12\x15\n\rconnection_id\x18\x01 \x01(\t\"D\n\x15\x43loseStatementRequest\x12\x15\n\rconnection_id\x18\x01 \x01(\t\x12\x14\n\x0cstatement_id\x18\x02 \x01(\r\"\x8b\x01\n\x15OpenConnectionRequest\x12\x15\n\rconnection_id\x18\x01 \x01(\t\x12.\n\x04info\x18\x02 \x03(\x0b\x32 .OpenConnectionRequest.InfoEntry\x1a+\n\tInfoEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"/\n\x16\x43loseConnectionRequest\x12\x15\n\rconnection_id\x18\x01 \x01(\t\"Y\n\x15\x43onnectionSyncRequest\x12\x15\n\rconnection_id\x18\x01 \x01(\t\x12)\n\nconn_props\x18\x02 \x01(\x0b\x32\x15.ConnectionProperties\"\xc7\x01\n\x0e\x45xecuteRequest\x12)\n\x0fstatementHandle\x18\x01 \x01(\x0b\x32\x10.StatementHandle\x12%\n\x10parameter_values\x18\x02 \x03(\x0b\x32\x0b.TypedValue\x12\'\n\x1f\x64\x65precated_first_frame_max_size\x18\x03 \x01(\x04\x12\x1c\n\x14has_parameter_values\x18\x04 \x01(\x08\x12\x1c\n\x14\x66irst_frame_max_size\x18\x05 \x01(\x05\"m\n\x12SyncResultsRequest\x12\x15\n\rconnection_id\x18\x01 \x01(\t\x12\x14\n\x0cstatement_id\x18\x02 \x01(\r\x12\x1a\n\x05state\x18\x03 \x01(\x0b\x32\x0b.QueryState\x12\x0e\n\x06offset\x18\x04 \x01(\x04\"&\n\rCommitRequest\x12\x15\n\rconnection_id\x18\x01 \x01(\t\"(\n\x0fRollbackRequest\x12\x15\n\rconnection_id\x18\x01 \x01(\t\"b\n\x1dPrepareAndExecuteBatchRequest\x12\x15\n\rconnection_id\x18\x01 \x01(\t\x12\x14\n\x0cstatement_id\x18\x02 \x01(\r\x12\x14\n\x0csql_commands\x18\x03 \x03(\t\"4\n\x0bUpdateBatch\x12%\n\x10parameter_values\x18\x01 \x03(\x0b\x32\x0b.TypedValue\"a\n\x13\x45xecuteBatchRequest\x12\x15\n\rconnection_id\x18\x01 \x01(\t\x12\x14\n\x0cstatement_id\x18\x02 \x01(\r\x12\x1d\n\x07updates\x18\x03 \x03(\x0b\x32\x0c.UpdateBatchB\"\n org.apache.calcite.avatica.protob\x06proto3')



_CATALOGSREQUEST = DESCRIPTOR.message_types_by_name['CatalogsRequest']
_DATABASEPROPERTYREQUEST = DESCRIPTOR.message_types_by_name['DatabasePropertyRequest']
_SCHEMASREQUEST = DESCRIPTOR.message_types_by_name['SchemasRequest']
_TABLESREQUEST = DESCRIPTOR.message_types_by_name['TablesRequest']
_TABLETYPESREQUEST = DESCRIPTOR.message_types_by_name['TableTypesRequest']
_COLUMNSREQUEST = DESCRIPTOR.message_types_by_name['ColumnsRequest']
_TYPEINFOREQUEST = DESCRIPTOR.message_types_by_name['TypeInfoRequest']
_PRIMARYKEYSREQUEST = DESCRIPTOR.message_types_by_name['PrimaryKeysRequest']
_IMPORTEDKEYSREQUEST = DESCRIPTOR.message_types_by_name['ImportedKeysRequest']
_EXPORTEDKEYSREQUEST = DESCRIPTOR.message_types_by_name['ExportedKeysRequest']
_INDEXINFOREQUEST = DESCRIPTOR.message_types_by_name['IndexInfoRequest']
_PREPAREANDEXECUTEREQUEST = DESCRIPTOR.message_types_by_name['PrepareAndExecuteRequest']
_PREPAREREQUEST = DESCRIPTOR.message_types_by_name['PrepareRequest']
_FETCHREQUEST = DESCRIPTOR.message_types_by_name['FetchRequest']
_CREATESTATEMENTREQUEST = DESCRIPTOR.message_types_by_name['CreateStatementRequest']
_CLOSESTATEMENTREQUEST = DESCRIPTOR.message_types_by_name['CloseStatementRequest']
_OPENCONNECTIONREQUEST = DESCRIPTOR.message_types_by_name['OpenConnectionRequest']
_OPENCONNECTIONREQUEST_INFOENTRY = _OPENCONNECTIONREQUEST.nested_types_by_name['InfoEntry']
_CLOSECONNECTIONREQUEST = DESCRIPTOR.message_types_by_name['CloseConnectionRequest']
_CONNECTIONSYNCREQUEST = DESCRIPTOR.message_types_by_name['ConnectionSyncRequest']
_EXECUTEREQUEST = DESCRIPTOR.message_types_by_name['ExecuteRequest']
_SYNCRESULTSREQUEST = DESCRIPTOR.message_types_by_name['SyncResultsRequest']
_COMMITREQUEST = DESCRIPTOR.message_types_by_name['CommitRequest']
_ROLLBACKREQUEST = DESCRIPTOR.message_types_by_name['RollbackRequest']
_PREPAREANDEXECUTEBATCHREQUEST = DESCRIPTOR.message_types_by_name['PrepareAndExecuteBatchRequest']
_UPDATEBATCH = DESCRIPTOR.message_types_by_name['UpdateBatch']
_EXECUTEBATCHREQUEST = DESCRIPTOR.message_types_by_name['ExecuteBatchRequest']
CatalogsRequest = _reflection.GeneratedProtocolMessageType('CatalogsRequest', (_message.Message,), {
  'DESCRIPTOR' : _CATALOGSREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:CatalogsRequest)
  })
_sym_db.RegisterMessage(CatalogsRequest)

DatabasePropertyRequest = _reflection.GeneratedProtocolMessageType('DatabasePropertyRequest', (_message.Message,), {
  'DESCRIPTOR' : _DATABASEPROPERTYREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:DatabasePropertyRequest)
  })
_sym_db.RegisterMessage(DatabasePropertyRequest)

SchemasRequest = _reflection.GeneratedProtocolMessageType('SchemasRequest', (_message.Message,), {
  'DESCRIPTOR' : _SCHEMASREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:SchemasRequest)
  })
_sym_db.RegisterMessage(SchemasRequest)

TablesRequest = _reflection.GeneratedProtocolMessageType('TablesRequest', (_message.Message,), {
  'DESCRIPTOR' : _TABLESREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:TablesRequest)
  })
_sym_db.RegisterMessage(TablesRequest)

TableTypesRequest = _reflection.GeneratedProtocolMessageType('TableTypesRequest', (_message.Message,), {
  'DESCRIPTOR' : _TABLETYPESREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:TableTypesRequest)
  })
_sym_db.RegisterMessage(TableTypesRequest)

ColumnsRequest = _reflection.GeneratedProtocolMessageType('ColumnsRequest', (_message.Message,), {
  'DESCRIPTOR' : _COLUMNSREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:ColumnsRequest)
  })
_sym_db.RegisterMessage(ColumnsRequest)

TypeInfoRequest = _reflection.GeneratedProtocolMessageType('TypeInfoRequest', (_message.Message,), {
  'DESCRIPTOR' : _TYPEINFOREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:TypeInfoRequest)
  })
_sym_db.RegisterMessage(TypeInfoRequest)

PrimaryKeysRequest = _reflection.GeneratedProtocolMessageType('PrimaryKeysRequest', (_message.Message,), {
  'DESCRIPTOR' : _PRIMARYKEYSREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:PrimaryKeysRequest)
  })
_sym_db.RegisterMessage(PrimaryKeysRequest)

ImportedKeysRequest = _reflection.GeneratedProtocolMessageType('ImportedKeysRequest', (_message.Message,), {
  'DESCRIPTOR' : _IMPORTEDKEYSREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:ImportedKeysRequest)
  })
_sym_db.RegisterMessage(ImportedKeysRequest)

ExportedKeysRequest = _reflection.GeneratedProtocolMessageType('ExportedKeysRequest', (_message.Message,), {
  'DESCRIPTOR' : _EXPORTEDKEYSREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:ExportedKeysRequest)
  })
_sym_db.RegisterMessage(ExportedKeysRequest)

IndexInfoRequest = _reflection.GeneratedProtocolMessageType('IndexInfoRequest', (_message.Message,), {
  'DESCRIPTOR' : _INDEXINFOREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:IndexInfoRequest)
  })
_sym_db.RegisterMessage(IndexInfoRequest)

PrepareAndExecuteRequest = _reflection.GeneratedProtocolMessageType('PrepareAndExecuteRequest', (_message.Message,), {
  'DESCRIPTOR' : _PREPAREANDEXECUTEREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:PrepareAndExecuteRequest)
  })
_sym_db.RegisterMessage(PrepareAndExecuteRequest)

PrepareRequest = _reflection.GeneratedProtocolMessageType('PrepareRequest', (_message.Message,), {
  'DESCRIPTOR' : _PREPAREREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:PrepareRequest)
  })
_sym_db.RegisterMessage(PrepareRequest)

FetchRequest = _reflection.GeneratedProtocolMessageType('FetchRequest', (_message.Message,), {
  'DESCRIPTOR' : _FETCHREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:FetchRequest)
  })
_sym_db.RegisterMessage(FetchRequest)

CreateStatementRequest = _reflection.GeneratedProtocolMessageType('CreateStatementRequest', (_message.Message,), {
  'DESCRIPTOR' : _CREATESTATEMENTREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:CreateStatementRequest)
  })
_sym_db.RegisterMessage(CreateStatementRequest)

CloseStatementRequest = _reflection.GeneratedProtocolMessageType('CloseStatementRequest', (_message.Message,), {
  'DESCRIPTOR' : _CLOSESTATEMENTREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:CloseStatementRequest)
  })
_sym_db.RegisterMessage(CloseStatementRequest)

OpenConnectionRequest = _reflection.GeneratedProtocolMessageType('OpenConnectionRequest', (_message.Message,), {

  'InfoEntry' : _reflection.GeneratedProtocolMessageType('InfoEntry', (_message.Message,), {
    'DESCRIPTOR' : _OPENCONNECTIONREQUEST_INFOENTRY,
    '__module__' : 'requests_pb2'
    # @@protoc_insertion_point(class_scope:OpenConnectionRequest.InfoEntry)
    })
  ,
  'DESCRIPTOR' : _OPENCONNECTIONREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:OpenConnectionRequest)
  })
_sym_db.RegisterMessage(OpenConnectionRequest)
_sym_db.RegisterMessage(OpenConnectionRequest.InfoEntry)

CloseConnectionRequest = _reflection.GeneratedProtocolMessageType('CloseConnectionRequest', (_message.Message,), {
  'DESCRIPTOR' : _CLOSECONNECTIONREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:CloseConnectionRequest)
  })
_sym_db.RegisterMessage(CloseConnectionRequest)

ConnectionSyncRequest = _reflection.GeneratedProtocolMessageType('ConnectionSyncRequest', (_message.Message,), {
  'DESCRIPTOR' : _CONNECTIONSYNCREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:ConnectionSyncRequest)
  })
_sym_db.RegisterMessage(ConnectionSyncRequest)

ExecuteRequest = _reflection.GeneratedProtocolMessageType('ExecuteRequest', (_message.Message,), {
  'DESCRIPTOR' : _EXECUTEREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:ExecuteRequest)
  })
_sym_db.RegisterMessage(ExecuteRequest)

SyncResultsRequest = _reflection.GeneratedProtocolMessageType('SyncResultsRequest', (_message.Message,), {
  'DESCRIPTOR' : _SYNCRESULTSREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:SyncResultsRequest)
  })
_sym_db.RegisterMessage(SyncResultsRequest)

CommitRequest = _reflection.GeneratedProtocolMessageType('CommitRequest', (_message.Message,), {
  'DESCRIPTOR' : _COMMITREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:CommitRequest)
  })
_sym_db.RegisterMessage(CommitRequest)

RollbackRequest = _reflection.GeneratedProtocolMessageType('RollbackRequest', (_message.Message,), {
  'DESCRIPTOR' : _ROLLBACKREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:RollbackRequest)
  })
_sym_db.RegisterMessage(RollbackRequest)

PrepareAndExecuteBatchRequest = _reflection.GeneratedProtocolMessageType('PrepareAndExecuteBatchRequest', (_message.Message,), {
  'DESCRIPTOR' : _PREPAREANDEXECUTEBATCHREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:PrepareAndExecuteBatchRequest)
  })
_sym_db.RegisterMessage(PrepareAndExecuteBatchRequest)

UpdateBatch = _reflection.GeneratedProtocolMessageType('UpdateBatch', (_message.Message,), {
  'DESCRIPTOR' : _UPDATEBATCH,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:UpdateBatch)
  })
_sym_db.RegisterMessage(UpdateBatch)

ExecuteBatchRequest = _reflection.GeneratedProtocolMessageType('ExecuteBatchRequest', (_message.Message,), {
  'DESCRIPTOR' : _EXECUTEBATCHREQUEST,
  '__module__' : 'requests_pb2'
  # @@protoc_insertion_point(class_scope:ExecuteBatchRequest)
  })
_sym_db.RegisterMessage(ExecuteBatchRequest)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n org.apache.calcite.avatica.proto'
  _OPENCONNECTIONREQUEST_INFOENTRY._options = None
  _OPENCONNECTIONREQUEST_INFOENTRY._serialized_options = b'8\001'
  _CATALOGSREQUEST._serialized_start=32
  _CATALOGSREQUEST._serialized_end=72
  _DATABASEPROPERTYREQUEST._serialized_start=74
  _DATABASEPROPERTYREQUEST._serialized_end=122
  _SCHEMASREQUEST._serialized_start=124
  _SCHEMASREQUEST._serialized_end=204
  _TABLESREQUEST._serialized_start=207
  _TABLESREQUEST._serialized_end=356
  _TABLETYPESREQUEST._serialized_start=358
  _TABLETYPESREQUEST._serialized_end=400
  _COLUMNSREQUEST._serialized_start=403
  _COLUMNSREQUEST._serialized_end=540
  _TYPEINFOREQUEST._serialized_start=542
  _TYPEINFOREQUEST._serialized_end=582
  _PRIMARYKEYSREQUEST._serialized_start=584
  _PRIMARYKEYSREQUEST._serialized_end=680
  _IMPORTEDKEYSREQUEST._serialized_start=682
  _IMPORTEDKEYSREQUEST._serialized_end=779
  _EXPORTEDKEYSREQUEST._serialized_start=781
  _EXPORTEDKEYSREQUEST._serialized_end=878
  _INDEXINFOREQUEST._serialized_start=881
  _INDEXINFOREQUEST._serialized_end=1012
  _PREPAREANDEXECUTEREQUEST._serialized_start=1015
  _PREPAREANDEXECUTEREQUEST._serialized_end=1176
  _PREPAREREQUEST._serialized_start=1178
  _PREPAREREQUEST._serialized_end=1277
  _FETCHREQUEST._serialized_start=1280
  _FETCHREQUEST._serialized_end=1408
  _CREATESTATEMENTREQUEST._serialized_start=1410
  _CREATESTATEMENTREQUEST._serialized_end=1457
  _CLOSESTATEMENTREQUEST._serialized_start=1459
  _CLOSESTATEMENTREQUEST._serialized_end=1527
  _OPENCONNECTIONREQUEST._serialized_start=1530
  _OPENCONNECTIONREQUEST._serialized_end=1669
  _OPENCONNECTIONREQUEST_INFOENTRY._serialized_start=1626
  _OPENCONNECTIONREQUEST_INFOENTRY._serialized_end=1669
  _CLOSECONNECTIONREQUEST._serialized_start=1671
  _CLOSECONNECTIONREQUEST._serialized_end=1718
  _CONNECTIONSYNCREQUEST._serialized_start=1720
  _CONNECTIONSYNCREQUEST._serialized_end=1809
  _EXECUTEREQUEST._serialized_start=1812
  _EXECUTEREQUEST._serialized_end=2011
  _SYNCRESULTSREQUEST._serialized_start=2013
  _SYNCRESULTSREQUEST._serialized_end=2122
  _COMMITREQUEST._serialized_start=2124
  _COMMITREQUEST._serialized_end=2162
  _ROLLBACKREQUEST._serialized_start=2164
  _ROLLBACKREQUEST._serialized_end=2204
  _PREPAREANDEXECUTEBATCHREQUEST._serialized_start=2206
  _PREPAREANDEXECUTEBATCHREQUEST._serialized_end=2304
  _UPDATEBATCH._serialized_start=2306
  _UPDATEBATCH._serialized_end=2358
  _EXECUTEBATCHREQUEST._serialized_start=2360
  _EXECUTEBATCHREQUEST._serialized_end=2457
# @@protoc_insertion_point(module_scope)