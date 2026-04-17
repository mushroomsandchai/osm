def command(filename, url, region, country):
    return(f"""
            mkdir -p /spark/files/{country}/
            cd /spark/files/{country}
            echo "Downloading {filename}"
            curl -fLs -o {filename} {url}
            echo "Exporting and cleaning {filename} to geojsonseq format"
            osmium export {filename} \
                --output-format=geojsonseq \
                --geometry-types=point \
                -o - | tr -d '\x1e' > {region}.geojsonseq
            rm {filename}
            echo "Exporting geojsonseq format to parquet after extracting the required fields"
            duckdb -c "
            copy (
                select
                    properties->>'$.name'          as name,
                    properties->>'$.amenity'       as amenity,
                    properties->>'$.shop'          as shop,
                    properties->>'$.leisure'       as leisure,
                    properties->>'$.opening_hours' as opening_hours,
                    geometry->'$.coordinates'      as coordinates
                from read_json('/spark/files/{country}/{region}.geojsonseq',
                    format='newline_delimited',
                    columns={{
                        type: 'varchar',
                        geometry: 'json',
                        properties: 'json'
                    }})
            ) to '/spark/files/{country}/{region}.parquet' (format parquet, compression snappy);
            "
            rm {region}.geojsonseq
    """)