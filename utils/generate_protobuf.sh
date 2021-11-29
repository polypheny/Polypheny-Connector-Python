#!/bin/bash
#
#   ADMIN UTILITY
#
# This script is only used during the development process and aids to recreated
# the protobug related python files which correspond to the RPC's server defined .proto files.

# You DO NOT need to invoke this script manually.
# This is only needed id the proto files on avatica-core-${VERSION}-POLYPHENY have changed



AUTHOR="Marc Hennemann"

AVATICA_VER=rel/avatica-1.17.2

set -e

#cleanup old environment
#rm -rf polypheny-avatica-tmp

#recreate new environemnt
#mkdir polypheny-avatica-tmp
#cd polypheny-avatica-tmp

#get latest version of polypheny-avatica
#wget -O polypheny-avatica.tar.gz https://github.com/apache/calcite-avatica/archive/$AVATICA_VER.tar.gz
#tar -x --strip-components=1 -f polypheny-avatica.tar.gz


cd ..
rm -f polypheny/avatica/protobuf/*_pb2.py
protoc --proto_path=polypheny-avatica-tmp/core/src/main/protobuf/ --python_out=polypheny/avatica/protobuf polypheny-avatica-tmp/core/src/main/protobuf/*.proto
protoc --proto_path=polypheny-avatica-tmp/ --python_out=polypheny/avatica/protobuf polypheny-avatica-tmp/*.proto
sed -i 's/import common_pb2/from . import common_pb2/' polypheny/avatica/protobuf/*_pb2.py

rm -rf polypheny-avatica-tmp
