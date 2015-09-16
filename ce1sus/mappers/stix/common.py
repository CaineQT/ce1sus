# -*- coding: utf-8 -*-

"""
(Description)

Created on 10 Sep 2015
"""

from ce1sus.db.classes.ccybox.common.time import CyboxTime
from ce1sus.db.classes.ccybox.core.observables import Observable, ObservableComposition
from ce1sus.db.classes.cstix.common.confidence import Confidence
from ce1sus.db.classes.cstix.common.datetimewithprecision import DateTimeWithPrecision
from ce1sus.db.classes.cstix.common.identity import Identity
from ce1sus.db.classes.cstix.common.information_source import InformationSource
from ce1sus.db.classes.cstix.common.kill_chains import KillChainPhaseReference
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.common.tools import ToolInformation
from ce1sus.db.classes.cstix.core.stix_header import STIXHeader, PackageIntent
from ce1sus.db.classes.cstix.data_marking import MarkingSpecification
from ce1sus.db.classes.cstix.extensions.marking.simple_markings import SimpleMarkingStructure
from ce1sus.db.classes.cstix.extensions.test_mechanism.yara_test_mechanism import YaraTestMechanism
from ce1sus.db.classes.cstix.indicator.indicator import Indicator, IndicatorType
from ce1sus.db.classes.cstix.indicator.sightings import Sighting
from ce1sus.db.classes.internal.event import Event
from ce1sus.db.classes.ccybox.common.measuresource import MeasureSource


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

# the map maps stix classes to ce1sus classes
CLASS_MAP = {'stix.core.stix_package.STIXPackage': Event,
             'stix.core.stix_header.STIXHeader': STIXHeader,
             'stix.data_marking.Marking': 'handle_markings',
             'stix.common.structured_text.StructuredText': StructuredText,
             'stix.core.stix_package.Indicators': 'handle_list',
             'stix.core.ttps.TTPs': 'handle_list',
             'stix.data_marking._MarkingStructures': 'handle_list',
             'stix.data_marking.MarkingSpecification': MarkingSpecification,
             'stix.extensions.marking.tlp.TLPMarkingStructure': 'set_tlp',
             'stix.extensions.marking.simple_marking.SimpleMarkingStructure': SimpleMarkingStructure,
             'stix.indicator.indicator.Indicator': Indicator,
             'stix.common.information_source.InformationSource': InformationSource,
             'stix.common.identity.Identity': Identity,
             'cybox.common.time.Time': CyboxTime,
             'cybox.common.datetimewithprecision.DateTimeWithPrecision': DateTimeWithPrecision,
             'stix.common.confidence.Confidence': Confidence,
             'stix.common.kill_chains.KillChainPhasesReference': 'handle_list',
             'cybox.core.observable.Observable': Observable,
             'cybox.core.observable.ObservableComposition': ObservableComposition,
             'stix.indicator.indicator.IndicatorTypes': 'handle_vocab_list',
             'stix.indicator.indicator._Observables': 'handle_list',
             'stix.common.vocabs.IndicatorType': IndicatorType,
             'stix.common.vocabs.HighMediumLow': 'direct_vocab',
             'stix.common.kill_chains.KillChainPhaseReference': KillChainPhaseReference,
             'cybox.core.object.Object': 'map_object',
             'stix.indicator.sightings.Sightings': 'handle_list',
             'stix.indicator.sightings.Sighting': Sighting,
             'stix.indicator.test_mechanism.TestMechanisms': 'handle_list',
             'stix.extensions.test_mechanism.yara_test_mechanism.YaraTestMechanism': YaraTestMechanism,
             'stix.common.EncodedCDATA': 'handle_encodedCDATA',
             'stix.core.stix_header._PackageIntents': 'handle_list',
             'stix.common.vocabs.PackageIntent': PackageIntent,
             'cybox.common.tools.ToolInformationList': 'handle_list',
             'cybox.common.tools.ToolInformation': ToolInformation,
             'cybox.common.measuresource.MeasureSource': MeasureSource,
             'cybox.common.structured_text.StructuredText': StructuredText
             }

def get_fqcn(instance):
  if instance:
    return '{0}.{1}'.format(instance.__module__, instance.__class__.__name__)

def relation_definitions():
  return {'Created': 'Specifies that this object created the related object.',
          'Created_By': 'Specifies that this object was created by the related object.',
          'Deleted': 'Specifies that this object deleted the related object.',
          'Deleted_By': 'Specifies that this object was deleted by the related object.',
          'Modified_Properties_Of': 'Specifies that this object modified the properties of the related object.',
          'Properties_Modified_By': 'Specifies that the properties of this object were modified by the related object.',
          'Read_From': 'Specifies that this object was read from the related object.',
          'Read_From_By': 'Specifies that this object was read from by the related object.',
          'Wrote_To': 'Specifies that this object wrote to the related object.',
          'Written_To_By': 'Specifies that this object was written to by the related object.',
          'Downloaded_From': 'Specifies that this object was downloaded from the related object.',
          'Downloaded_To': 'Specifies that this object downloaded the related object.',
          'Downloaded': 'Specifies that this object downloaded the related object.',
          'Downloaded_By': 'Specifies that this object was downloaded by the related object.',
          'Uploaded': 'Specifies that this object uploaded the related object.',
          'Uploaded_By': 'Specifies that this object was uploaded by the related object.',
          'Uploaded_To': 'Specifies that this object was uploaded to the related object.',
          'Received_Via_Upload': 'Specifies that this object received the related object via upload.',
          'Uploaded_From': 'Specifies that this object was uploaded from the related object.',
          'Sent_Via_Upload': 'Specifies that this object sent the related object via upload.',
          'Suspended': 'Specifies that this object suspended the related object.',
          'Suspended_By': 'Specifies that this object was suspended by the related object.',
          'Paused': 'Specifies that this object paused the related object.',
          'Paused_By': 'Specifies that this object was paused by the related object.',
          'Resumed': 'Specifies that this object resumed the related object.',
          'Resumed_By': 'Specifies that this object was resumed by the related object.',
          'Opened': 'Specifies that this object opened the related object.',
          'Opened_By': 'Specifies that this object was opened by the related object.',
          'Closed': 'Specifies that this object closed the related object.',
          'Closed_By': 'Specifies that this object was closed by the related object.',
          'Copied_From': 'Specifies that this object was copied from the related object.',
          'Copied_To': 'Specifies that this object was copied to the related object.',
          'Copied': 'Specifies that this object copied the related object.',
          'Copied_By': 'Specifies that this object was copied by the related object.',
          'Moved_From': 'Specifies that this object was moved from the related object.',
          'Moved_To': 'Specifies that this object was moved to the related object.',
          'Moved': 'Specifies that this object moved the related object.',
          'Moved_By': 'Specifies that this object was moved by the related object.',
          'Searched_For': 'Specifies that this object searched for the related object.',
          'Searched_For_By': 'Specifies that this object was searched for by the related object.',
          'Allocated': 'Specifies that this object allocated the related object.',
          'Allocated_By': 'Specifies that this object was allocated by the related object.',
          'Initialized_To': 'Specifies that this object was initialized to the related object.',
          'Initialized_By': 'Specifies that this object was initialized by the related object.',
          'Sent': 'Specifies that this object sent the related object.',
          'Sent_By': 'Specifies that this object was sent by the related object.',
          'Sent_To': 'Specifies that this object was sent to the related object.',
          'Received_From': 'Specifies that this object was received from the related object.',
          'Received': 'Specifies that this object received the related object.',
          'Received_By': 'Specifies that this object was received by the related object.',
          'Mapped_Into': 'Specifies that this object was mapped into the related object.',
          'Mapped_By': 'Specifies that this object was mapped by the related object.',
          'Properties_Queried': 'Specifies that the object queried properties of the related object.',
          'Properties_Queried_By': 'Specifies that the properties of this object were queried by the related object.',
          'Values_Enumerated': 'Specifies that the object enumerated values of the related object.',
          'Values_Enumerated_By': 'Specifies that the values of the object were enumerated by the related object.',
          'Bound': 'Specifies that this object bound the related object.',
          'Bound_By': 'Specifies that this object was bound by the related object.',
          'Freed': 'Specifies that this object freed the related object.',
          'Freed_By': 'Specifies that this object was freed by the related object.',
          'Killed': 'Specifies that this object killed the related object.',
          'Killed_By': 'Specifies that this object was killed by the related object.',
          'Encrypted': 'Specifies that this object encrypted the related object.',
          'Encrypted_By': 'Specifies that this object was encrypted by the related object.',
          'Encrypted_To': 'Specifies that this object was encrypted to the related object.',
          'Encrypted_From': 'Specifies that this object was encrypted from the related object.',
          'Decrypted': 'Specifies that this object decrypted the related object.',
          'Decrypted_By': 'Specifies that this object was decrypted by the related object.',
          'Packed': 'Specifies that this object packed the related object.',
          'Packed_By': 'Specifies that this object was packed by the related object.',
          'Unpacked': 'Specifies that this object unpacked the related object.',
          'Unpacked_By': 'Specifies that this object was unpacked by the related object.',
          'Packed_From': 'Specifies that this object was packed from the related object.',
          'Packed_Into': 'Specifies that this object was packed into the related object.',
          'Encoded': 'Specifies that this object encoded the related object.',
          'Encoded_By': 'Specifies that this object was encoded by the related object.',
          'Decoded': 'Specifies that this object decoded the related object.',
          'Decoded_By': 'Specifies that this object was decoded by the related object.',
          'Compressed_From': 'Specifies that this object was compressed from the related object.',
          'Compressed_Into': 'Specifies that this object was compressed into the related object.',
          'Compressed': 'Specifies that this object compressed the related object.',
          'Compressed_By': 'Specifies that this object was compressed by the related object.',
          'Decompressed': 'Specifies that this object decompressed the related object.',
          'Decompressed_By': 'Specifies that this object was decompressed by the related object.',
          'Joined': 'Specifies that this object joined the related object.',
          'Joined_By': 'Specifies that this object was joined by the related object.',
          'Merged': 'Specifies that this object merged the related object.',
          'Merged_By': 'Specifies that this object was merged by the related object.',
          'Locked': 'Specifies that this object locked the related object.',
          'Locked_By': 'Specifies that this object was locked by the related object.',
          'Unlocked': 'Specifies that this object unlocked the related object.',
          'Unlocked_By': 'Specifies that this object was unlocked by the related object.',
          'Hooked': 'Specifies that this object hooked the related object.',
          'Hooked_By': 'Specifies that this object was hooked by the related object.',
          'Unhooked': 'Specifies that this object unhooked the related object.',
          'Unhooked_By': 'Specifies that this object was unhooked by the related object.',
          'Monitored': 'Specifies that this object monitored the related object.',
          'Monitored_By': 'Specifies that this object was monitored by the related object.',
          'Listened_On': 'Specifies that this object listened on the related object.',
          'Listened_On_By': 'Specifies that this object was listened on by the related object.',
          'Renamed_From': 'Specifies that this object was renamed from the related object.',
          'Renamed_To': 'Specifies that this object was renamed to the related object.',
          'Renamed': 'Specifies that this object renamed the related object.',
          'Renamed_By': 'Specifies that this object was renamed by the related object.',
          'Injected_Into': 'Specifies that this object injected into the related object.',
          'Injected_As': 'Specifies that this object injected as the related object.',
          'Injected': 'Specifies that this object injected the related object.',
          'Injected_By': 'Specifies that this object was injected by the related object.',
          'Deleted_From': 'Specifies that this object was deleted from the related object.',
          'Previously_Contained': 'Specifies that this object previously contained the related object.',
          'Loaded_Into': 'Specifies that this object loaded into the related object.',
          'Loaded_From': 'Specifies that this object was loaded from the related object.',
          'Set_To': 'Specifies that this object was set to the related object.',
          'Set_From': 'Specifies that this object was set from the related object.',
          'Resolved_To': 'Specifies that this object was resolved to the related object.',
          'Related_To': 'Specifies that this object is related to the related object.',
          'Dropped': 'Specifies that this object dropped the related object.',
          'Dropped_By': 'Specifies that this object was dropped by the related object.',
          'Contains': 'Specifies that this object contains the related object.',
          'Contained_Within': 'Specifies that this object is contained within the related object.',
          'Extracted_From': 'Specifies that this object was extracted from the related object.',
          'Installed': 'Specifies that this object installed the related object.',
          'Installed_By': 'Specifies that this object was installed by the related object.',
          'Connected_To': 'Specifies that this object connected to the related object.',
          'Connected_From': 'Specifies that this object was connected to from the related object.',
          'Sub-domain_Of': 'Specifies that this object is a sub-domain of the related object.',
          'Supra-domain_Of': 'Specifies that this object is a supra-domain of the related object.',
          'Root_Domain_Of': 'Specifies that this object is the root domain of the related object.',
          'FQDN_Of': 'Specifies that this object is an FQDN of the related object.',
          'Parent_Of': 'Specifies that this object is a parent of the related object.',
          'Child_Of': 'Specifies that this object is a child of the related object.',
          'Characterizes': 'Specifies that this object describes the properties of the related object. This is most applicable in cases where the related object is an Artifact Object and this object is a non-Artifact Object.',
          'Characterized_By': 'Specifies that the related object describes the properties of this object. This is most applicable in cases where the related object is a non-Artifact Object and this object is an Artifact Object.',
          'Used': 'Specifies that this object used the related object.',
          'Used_By': 'Specifies that this object was used by the related object.',
          'Redirects_To': 'Specifies that this object redirects to the related object.'}
