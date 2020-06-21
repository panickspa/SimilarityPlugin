Plugin Calculation Method
=============
Calculation method is stored in SimilarityPlugin Class as its method

.. toctree::
   :maxdepth: 2


calcMapCurvesGeom
------------------------------   
   .. py:attribute:: calcMapCurvesGeom (self, g:QgsGeometry, g2:QgsGeometry)
         
      Calculate the score between the geometry in float number using GOF Mapcurves (Hargrove et al. 2006)
      
      :param SimilarityPlugin self: class parent
      :param QgsGeometry g: first geometry will be checked
      :param QgsGeometry g2: second geometry will be checked
      :return: float

calcMapCurves
--------------------------------
   .. py:attribute:: calcMapCurves (self, feature:QgsFeature, feature2:QgsFeature)
         
      Calculate the score and save to self.similarLayer. Score saved in float number using GOF Mapcurves (Hargrove et al. 2006)
      
      :param SimilarityPlugin self: class parent
      :param QgsFeature feature: first feature will be checked
      :param QgsFeature feature2: second feature will be checked
      :return: null

calcSq
-----------------------------
   .. py:attribute:: calcSq (self, layer:QgsVectorLayer, layer2:QgsVectorLayer)
         
      Checking similarity between two layer with squential method
      
      :param SimilarityPlugin self: class parent
      :param QgsVectorLayer layer: first layer will checked
      :param QgsVectorLayer layer2: second layer will checked
      :return: null

calcKNN
----------------------------------------------
   .. py:attribute:: calcKNN (self, layer:QgsVectorLayer, layer2:QgsVectorLayer)
         
      Check each feature between 2 layer within radius bounding box. Radius distance using euclidean.

      :param SimilarityPlugin self: class parent
      :param QgsVectorLayer layer: first layer will checked
      :param QgsVectorLayer layer2: second layer will checked
      :return: null

calcWK
----------------------------------------------
   .. py:attribute:: calcWK (self, layer:QgsVectorLayer, layer2:QgsVectorLayer)
         
      Match each feature the primary key in map, see https://sig.bps.go.id/

      :param SimilarityPlugin self: class parent
      :param QgsVectorLayer layer: first layer will checked
      :param QgsVectorLayer layer2: second layer will checked
      :return: null

translateCenterGeom
-----------------------------------------------
   .. py:attribute:: translateCenterGeom (self, g:QgsGeometry, target:QgsGeometry)

      Translate first geometry to the center of target geometry

      :param SimilarityPlugin self: class parent
      :param QgsVectorLayer layer: first layer will checked
      :param QgsVectorLayer layer2: second layer will checked
      :return: QgsGeometry
