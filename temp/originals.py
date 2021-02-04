    @api.multi
    def product_meli_get_product( self ):
        company = self.env.user.company_id
        product_obj = self.env['product.product']
        uomobj = self.env[uom_model]
        #pdb.set_trace()
        product = self

        _logger.info("product_meli_get_product")
        _logger.info(product.default_code)

        product_template_obj = self.env['product.template']
        product_template = product_template_obj.browse(product.product_tmpl_id.id)

        CLIENT_ID = company.mercadolibre_client_id
        CLIENT_SECRET = company.mercadolibre_secret_key
        ACCESS_TOKEN = company.mercadolibre_access_token
        REFRESH_TOKEN = company.mercadolibre_refresh_token

        meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)

        try:
            response = meli.get("/items/"+product.meli_id, {'access_token':meli.access_token})
            _logger.info('meli.get(/items/product.meli_id): ')
            _logger.info(response)
            rjson = response.json()
            _logger.info('meli.get(/items/product.meli_id) response.json(): ')
            _logger.info(rjson)
        except IOError as e:
            _logger.error( "I/O error({0}): {1}".format(e.errno, e.strerror) )
            return {}
        except:
            _logger.error( "Rare error" )
            return {}
        des = ''
        desplain = ''
        vid = ''
        if 'error' in rjson:
            return {}

        #if "content" in response:
        #    _logger.info(response.content)
        #    _logger.info( "product_meli_get_product > response.content: " + response.content )

        #TODO: traer la descripcion: con
        #https://api.mercadolibre.com/items/{ITEM_ID}/description?access_token=$ACCESS_TOKEN
        if rjson and rjson['descriptions']:
            response2 = meli.get("/items/"+product.meli_id+"/description", {'access_token':meli.access_token})
            rjson2 = response2.json()
            if 'text' in rjson2:
               des = rjson2['text']
            if 'plain_text' in rjson2:
               desplain = rjson2['plain_text']
            if (len(des)>0):
                desplain = des

        #TODO: verificar q es un video
        if rjson['video_id']:
            vid = ''

        #TODO: traer las imagenes
        #TODO:
        pictures = rjson['pictures']
        if pictures and len(pictures):
            product._meli_set_images(product_template, pictures)

        #categories
        product._meli_set_category( product_template, rjson['category_id'] )

        imagen_id = ''
        meli_dim_str = ''
        if ('dimensions' in rjson):
            if (rjson['dimensions']):
                meli_dim_str = rjson['dimensions']

        if ('pictures' in rjson):
            if (len(rjson['pictures'])>0):
                imagen_id = rjson['pictures'][0]['id']

        try:
            if (float(rjson['price'])>=0.0):
                product._meli_set_product_price( product_template, rjson['price'] )
        except:
            rjson['price'] = 0.0

        meli_fields = {
            'name': rjson['title'].encode("utf-8"),
            #'default_code': rjson['id'],
            'meli_imagen_id': imagen_id,
            #'meli_post_required': True,
            'meli_id': rjson['id'],
            'meli_permalink': rjson['permalink'],
            'meli_title': rjson['title'].encode("utf-8"),
            'meli_description': desplain,
            'meli_listing_type': rjson['listing_type_id'],
            'meli_buying_mode':rjson['buying_mode'],
            'meli_price': str(rjson['price']),
            'meli_price_fixed': True,
            'meli_currency': rjson['currency_id'],
            'meli_condition': rjson['condition'],
            'meli_available_quantity': rjson['available_quantity'],
            'meli_warranty': rjson['warranty'],
            'meli_imagen_link': rjson['thumbnail'],
            'meli_video': str(vid),
            'meli_dimensions': meli_dim_str,
        }

        tmpl_fields = {
          'name': meli_fields["name"],
          'description_sale': desplain,
          #'name': str(rjson['id']),
          #'lst_price': ml_price_convert,
          'meli_title': meli_fields["meli_title"],
          'meli_description': meli_fields["meli_description"],
          #'meli_category': meli_fields["meli_category"],
          'meli_listing_type': meli_fields["meli_listing_type"],
          'meli_buying_mode': meli_fields["meli_buying_mode"],
          'meli_price': meli_fields["meli_price"],
          'meli_currency': meli_fields["meli_currency"],
          'meli_condition': meli_fields["meli_condition"],
          'meli_warranty': meli_fields["meli_warranty"],
          'meli_dimensions': meli_fields["meli_dimensions"]
        }

        if (product.name and not company.mercadolibre_overwrite_variant):
            del meli_fields['name']
        if (product_template.name and not company.mercadolibre_overwrite_template):
            del tmpl_fields['name']
        if (product_template.description_sale and not company.mercadolibre_overwrite_template):
            del tmpl_fields['description_sale']

        product.write( meli_fields )
        product_template.write( tmpl_fields )

        if (rjson['available_quantity']>=0):
            if (product_template.type not in ['product']):
                try:
                    product_template.write( { 'type': 'product' } )
                except Exception as e:
                    _logger.info("Set type almacenable ('product') not possible:")
                    _logger.error(e, exc_info=True)
                    pass;
            #TODO: agregar parametro para esto: ml_auto_website_published_if_available  default true
            if (1==1 and rjson['available_quantity']>0):
                product_template.website_published = True

        #TODO: agregar parametro para esto: ml_auto_website_unpublished_if_not_available default false
        if (1==2 and rjson['available_quantity']==0):
            product_template.website_published = False

        posting_fields = {
            'posting_date': str(datetime.now()),
            'meli_id':rjson['id'],
            'product_id':product.id,
            'name': 'Post ('+str(product.meli_id)+'): ' + product.meli_title
        }

        posting = self.env['mercadolibre.posting'].search([('meli_id','=',rjson['id'])])
        posting_id = posting.id

        if not posting_id:
            posting = self.env['mercadolibre.posting'].create((posting_fields))
            posting_id = posting.id
            if (posting):
                posting.posting_query_questions()
        else:
            posting.write({'product_id':product.id })
            posting.posting_query_questions()


        b_search_nonfree_ship = False
        if ('shipping' in rjson):
            att_shipping = {
                'name': 'Con envío',
                'create_variant': default_no_create_variant
            }
            if ('variations' in rjson):
                #_logger.info("has variations")
                pass
            else:
                rjson['variations'] = []

            if ('free_methods' in rjson['shipping']):
                att_shipping['value_name'] = 'Sí'
                #buscar referencia del template correspondiente
                b_search_nonfree_ship = True
            else:
                att_shipping['value_name'] = 'No'

            rjson['variations'].append({'attribute_combinations': [ att_shipping ]})

        #_logger.info(rjson['variations'])
        published_att_variants = False
        if ('variations' in rjson):
            #recorrer los variations>attribute_combinations y agregarlos como atributos de las variantes
            #_logger.info(rjson['variations'])
            vindex = -1
            for variation in rjson['variations']:
                vindex = vindex + 1
                if ('attribute_combinations' in variation):
                    _attcomb_str = ""
                    rjson['variations'][vindex]["default_code"] = ""
                    for attcomb in variation['attribute_combinations']:
                        namecap = attcomb['name']
                        if (len(namecap)):
                            att = {
                                'name': namecap,
                                'value_name': attcomb['value_name'],
                                'create_variant': default_create_variant,
                                'att_id': False
                            }
                            if ('id' in attcomb):
                                if (attcomb["id"]):
                                    if (len(attcomb["id"])):
                                        att["att_id"] = attcomb["id"]
                            if (att["att_id"]==False):
                                namecap = namecap.strip()
                                namecap = namecap[0].upper()+namecap[1:]
                                att["name"] = namecap
                            if ('create_variant' in attcomb):
                                att['create_variant'] = attcomb['create_variant']
                            else:
                                rjson['variations'][vindex]["default_code"] = rjson['variations'][vindex]["default_code"]+namecap+":"+attcomb['value_name']+";"
                            #_logger.info(att)
                            if (att["att_id"]):
                                # ML Attribute , we could search first...
                                #attribute = self.env['product.attribute'].search([('name','=',att['name']),('meli_default_id_attribute','!=',False)])
                                #if (len(attribute)==0):
                                # ningun atributo con ese nombre asociado
                                ml_attribute = self.env['mercadolibre.category.attribute'].search([('att_id','=',att['att_id'])])
                                attribute = []
                                if (len(ml_attribute)==1):
                                    attribute = self.env['product.attribute'].search([('meli_default_id_attribute','=',ml_attribute.id)])
                                if (len(attribute)==0):
                                    attribute = self.env['product.attribute'].search([('name','=',att['name'])])
                            else:
                                #customizado
                                #_logger.info("Atributo customizado:"+str(namecap))
                                attribute = self.env['product.attribute'].search([('name','=',namecap),('meli_default_id_attribute','=',False)])
                                _logger.info(attribute)

                                if (attcomb['name']!=namecap):
                                    attribute_duplicates = self.env['product.attribute'].search([('name','=',attcomb['name']),('meli_default_id_attribute','=',False)])
                                    _logger.info("attribute_duplicates:")
                                    _logger.info(attribute_duplicates)
                                    if (len(attribute_duplicates)>=1):
                                        #archive
                                        _logger.info("attribute_duplicates:",len(attribute_duplicates))
                                        for attdup in attribute_duplicates:
                                            _logger.info("duplicate:"+attdup.name+":"+str(attdup.id))
                                            attdup_line =  self.env[prod_att_line].search([('attribute_id','=',attdup.id),('product_tmpl_id','=',product_template.id)])
                                            if (len(attdup_line)):
                                                for attline in attdup_line:
                                                    attline.unlink()

                                #buscar en las lineas existentes
                                if (len(attribute)>1):
                                    att_line = self.env[prod_att_line].search([('attribute_id','in',attribute.ids),('product_tmpl_id','=',product_template.id)])
                                    _logger.info(att_line)
                                    if (len(att_line)):
                                        _logger.info("Atributo ya asignado!")
                                        attribute = att_line.attribute_id

                            attribute_id = False
                            if (len(attribute)==1):
                                attribute_id = attribute.id
                            elif (len(attribute)>1):
                                _logger.error("Attributes duplicated names!!!")
                                attribute_id = attribute[0].id

                            #_logger.info(attribute_id)
                            if attribute_id:
                                #_logger.info(attribute_id)
                                pass
                            else:
                                #_logger.info("Creating attribute:")
                                attribute_id = self.env['product.attribute'].create({ 'name': att['name'],'create_variant': att['create_variant'] }).id

                            if (att['create_variant']==default_create_variant):
                                #_logger.info("published_att_variants")
                                published_att_variants = True

                            if (attribute_id):
                                #_logger.info("Publishing attribute")
                                attribute_value_id = self.env['product.attribute.value'].search([('attribute_id','=',attribute_id),('name','=',att['value_name'])]).id
                                #_logger.info(_logger.info(attribute_id))
                                if attribute_value_id:
                                    #_logger.info(attribute_value_id)
                                    pass
                                else:
                                    _logger.info("Creating attribute value:"+str(att))
                                    if (att['value_name']!=None):
                                        attribute_value_id = self.env['product.attribute.value'].create({'attribute_id': attribute_id,'name': att['value_name']}).id

                                if (attribute_value_id):
                                    #_logger.info("attribute_value_id:")
                                    #_logger.info(attribute_value_id)
                                    #search for line ids.
                                    attribute_line =  self.env[prod_att_line].search([('attribute_id','=',attribute_id),('product_tmpl_id','=',product_template.id)])
                                    #_logger.info(attribute_line)
                                    if (attribute_line and attribute_line.id):
                                        #_logger.info(attribute_line)
                                        pass
                                    else:
                                        #_logger.info("Creating att line id:")
                                        att_vals = prepare_attribute( product_template.id, attribute_id, attribute_value_id )
                                        attribute_line =  self.env[prod_att_line].create(att_vals)

                                    if (attribute_line):
                                        #_logger.info("Check attribute line values id.")
                                        #_logger.info("attribute_line:")
                                        #_logger.info(attribute_line)
                                        if (attribute_line.value_ids):
                                            #check if values
                                            #_logger.info("Has value ids:")
                                            #_logger.info(attribute_line.value_ids.ids)
                                            if (attribute_value_id in attribute_line.value_ids.ids):
                                                #_logger.info(attribute_line.value_ids.ids)
                                                pass
                                            else:
                                                #_logger.info("Adding value id")
                                                attribute_line.value_ids = [(4,attribute_value_id)]
                                        else:
                                            #_logger.info("Adding value id")
                                            attribute_line.value_ids = [(4,attribute_value_id)]

        #_logger.info("product_uom_id")
        product_uom_id = uomobj.search([('name','=','Unidad(es)')])
        if (product_uom_id.id==False):
            product_uom_id = 1
        else:
            product_uom_id = product_uom_id.id

        _product_id = product.id
        _product_name = product.name
        _product_meli_id = product.meli_id

        #this write pull the trigger for create_variant_ids()...
        #_logger.info("rewrite to create variants")
        product_template.write({ 'attribute_line_ids': product_template.attribute_line_ids  })
        #_logger.info("published_att_variants:"+str(published_att_variants))
        if (published_att_variants):
            product_template.meli_pub_as_variant = True

            #_logger.info("Auto check product.template meli attributes to publish")
            for line in  product_template.attribute_line_ids:
                if (line.id not in product_template.meli_pub_variant_attributes.ids):
                    if (line.attribute_id.create_variant):
                        product_template.meli_pub_variant_attributes = [(4,line.id)]

            #_logger.info("check variants")
            for variant in product_template.product_variant_ids:
                #_logger.info("Created variant:")
                #_logger.info(variant)
                variant.meli_pub = product_template.meli_pub
                variant.meli_id = rjson['id']
                #variant.default_code = rjson['id']
                #variant.name = rjson['title'].encode("utf-8")
                has_sku = False

                _v_default_code = ""
                for att in att_value_ids(variant):
                    _v_default_code = _v_default_code + att.attribute_id.name+':'+att.name+';'
                #_logger.info("_v_default_code: " + _v_default_code)
                for variation in rjson['variations']:
                    #_logger.info(variation)
                    #_logger.info("variation[default_code]: " + variation["default_code"])
                    if (len(variation["default_code"]) and (variation["default_code"] in _v_default_code)):
                        if ("seller_custom_field" in variation):
                            #_logger.info("has_sku")
                            #_logger.info(variation["seller_custom_field"])
                            variant.default_code = variation["seller_custom_field"]
                            variant.meli_id_variation = variation["id"]
                            has_sku = True
                        else:
                            variant.default_code = variant.meli_id+'-'+_v_default_code
                        variant.meli_available_quantity = variation["available_quantity"]

                if (has_sku):
                    variant.set_bom()

                #_logger.info('meli_pub_principal_variant')
                #_logger.info(product_template.meli_pub_principal_variant.id)
                if (product_template.meli_pub_principal_variant.id is False):
                    #_logger.info("meli_pub_principal_variant set!")
                    product_template.meli_pub_principal_variant = variant
                    product = variant

                if (_product_id==variant.id):
                    product = variant
        else:
            #NO TIENE variantes pero tiene SKU
            if ("seller_custom_field" in rjson):
                if (rjson["seller_custom_field"]):
                    product.default_code = rjson["seller_custom_field"]
                product.set_bom()


        if (company.mercadolibre_update_local_stock):
            product_template.type = 'product'

            if (len(product_template.product_variant_ids)):
                for variant in product_template.product_variant_ids:

                    _product_id = variant.id
                    _product_name = variant.name
                    _product_meli_id = variant.meli_id

                    if (variant.meli_available_quantity != variant.virtual_available):
                        variant.product_update_stock(variant.meli_available_quantity)
            else:
                product.product_update_stock(product.meli_available_quantity)

        if ('attributes' in rjson):
            if (len(rjson['attributes']) and 1==1):
                for att in rjson['attributes']:
                    try:
                        _logger.info(att)
                        ml_attribute = self.env['mercadolibre.category.attribute'].search([('att_id','=',att['id'])])
                        attribute = []

                        if (ml_attribute and ml_attribute.id):
                            #_logger.info(ml_attribute)
                            attribute = self.env['product.attribute'].search([('meli_default_id_attribute','=',ml_attribute.id)])
                            #_logger.info(attribute)

                        if (len(attribute) and attribute.id):
                            attribute_id = attribute.id
                            attribute_value_id = self.env['product.attribute.value'].search([('attribute_id','=',attribute_id), ('name','=',att['value_name'])]).id
                            #_logger.info(_logger.info(attribute_id))
                            if attribute_value_id:
                                #_logger.info(attribute_value_id)
                                pass
                            else:
                                _logger.info("Creating attribute value:")
                                _logger.info(att)
                                if (att['value_name']!=None):
                                    attribute_value_id = self.env['product.attribute.value'].create({'attribute_id': attribute_id, 'name': att['value_name'] }).id

                            if (attribute_value_id):
                                attribute_line =  self.env[prod_att_line].search([('attribute_id','=',attribute_id),('product_tmpl_id','=',product_template.id)])
                                if (attribute_line and attribute_line.id):
                                    #_logger.info(attribute_line)
                                    pass
                                else:
                                    #_logger.info("Creating att line id:")
                                    att_vals = prepare_attribute( product_template.id, attribute_id, attribute_value_id )
                                    attribute_line =  self.env[prod_att_line].create(att_vals)

                                if (attribute_line):
                                    #_logger.info("Check attribute line values id.")
                                    #_logger.info("attribute_line:")
                                    #_logger.info(attribute_line)
                                    if (attribute_line.value_ids):
                                        #check if values
                                        #_logger.info("Has value ids:")
                                        #_logger.info(attribute_line.value_ids.ids)
                                        if (attribute_value_id in attribute_line.value_ids.ids):
                                            #_logger.info(attribute_line.value_ids.ids)
                                            pass
                                        else:
                                            #_logger.info("Adding value id")
                                            attribute_line.value_ids = [(4,attribute_value_id)]
                                    else:
                                        #_logger.info("Adding value id")
                                        attribute_line.value_ids = [(4,attribute_value_id)]
                    except Exception as e:
                        _logger.info("Attributes exception:")
                        _logger.info(e, exc_info=True)

        return {}