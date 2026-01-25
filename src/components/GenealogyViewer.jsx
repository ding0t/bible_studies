import React, { useState, useMemo } from 'react';
import { zadokToGregorian, gregorianToZadok } from '../utils/calendarConvert';
import { BibleReference } from './BibleReference';
import { colors } from '../styles/colors';
import genealogyIndex from '../data/genealogy/index.json';
import antediluvian from '../data/genealogy/antediluvian.json';
import patriarchal from '../data/genealogy/patriarchal.json';
import conquestJudges from '../data/genealogy/conquest-judges.json';
import dividedKingdom from '../data/genealogy/divided-kingdom.json';
import exileReturn from '../data/genealogy/exile-return.json';
import secondTemple from '../data/genealogy/second-temple.json';

// Merge all era data into a single structure
const mergeGenealogyData = () => {
  const people = [
    ...antediluvian.people,
    ...patriarchal.people,
    ...conquestJudges.people,
    ...dividedKingdom.people,
    ...exileReturn.people,
    ...secondTemple.people
  ];
  return {
    metadata: genealogyIndex.metadata,
    lineages: genealogyIndex.lineages,
    people: people
  };
};

const genealogyData = mergeGenealogyData();

const GenealogyViewer = () => {
  const [activeTab, setActiveTab] = useState('tree');
  const [selectedPersonId, setSelectedPersonId] = useState('abraham');
  const [selectedLineage, setSelectedLineage] = useState('jesus_line');
  const [calendarView, setCalendarView] = useState('gregorian');
  const [expandedNodes, setExpandedNodes] = useState(new Set(['noah', 'abraham']));
  const [filterEra, setFilterEra] = useState('all');
  const [filterGender, setFilterGender] = useState('all');
  const [filterName, setFilterName] = useState('');
  const [livingYearQuery, setLivingYearQuery] = useState('');
  const [ganttZoom, setGanttZoom] = useState(1);

  // Get person by ID
  const getPerson = (id) => genealogyData.people.find(p => p.id === id);

  // Get children of a person
  const getChildren = (personId) => {
    const person = getPerson(personId);
    return person?.children.map(childId => getPerson(childId)) || [];
  };

  // Get ancestors of a person (parents, grandparents, etc.)
  const getAncestors = (personId, ancestors = []) => {
    const person = getPerson(personId);
    if (!person || !person.parent_id) return ancestors;
    const parent = getPerson(person.parent_id);
    return parent ? getAncestors(parent.id, [parent, ...ancestors]) : ancestors;
  };

  // Get lineage path for a person
  const getLineagePath = (personId) => {
    const path = [getPerson(personId)];
    let current = getPerson(personId);
    while (current?.parent_id) {
      current = getPerson(current.parent_id);
      path.unshift(current);
    }
    return path;
  };

  // Filter people by era, gender, and name
  const filteredPeople = useMemo(() => {
    let filtered = genealogyData.people;
    
    // Filter by era
    if (filterEra !== 'all') {
      filtered = filtered.filter(p => p.era === filterEra);
    }
    
    // Filter by gender
    if (filterGender !== 'all') {
      filtered = filtered.filter(p => p.gender === filterGender);
    }
    
    // Filter by name (case-insensitive)
    if (filterName.trim() !== '') {
      const searchTerm = filterName.toLowerCase();
      filtered = filtered.filter(p => 
        p.name.toLowerCase().includes(searchTerm) || 
        (p.name_hebrew && p.name_hebrew.includes(filterName)) ||
        (p.name_transliteration && p.name_transliteration.toLowerCase().includes(searchTerm))
      );
    }
    
    return filtered;
  }, [filterEra, filterGender, filterName]);

  // Find people alive in a given year
  const getPeopleAliveInYear = (year, sourceCalendar = 'gregorian') => {
    const gregorianYear = sourceCalendar === 'gregorian' ? year : zadokToGregorian(year);
    return filteredPeople.filter(person => {
      const born = person.gregorian_year_born;
      const died = person.gregorian_year_died;
      if (born === null || died === null) return false;
      return born <= gregorianYear && gregorianYear <= died;
    });
  };

  // Toggle node expansion in tree
  const toggleExpanded = (personId) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(personId)) {
      newExpanded.delete(personId);
    } else {
      newExpanded.add(personId);
    }
    setExpandedNodes(newExpanded);
  };

  // Tree Node Component
  const TreeNode = ({ person, depth = 0 }) => {
    const isExpanded = expandedNodes.has(person.id);
    const children = getChildren(person.id);
    const hasChildren = children.length > 0;

    return (
      <div style={{ marginLeft: `${depth * 20}px` }} className="tree-node">
        <div
          className={`person-row ${selectedPersonId === person.id ? 'selected' : ''}`}
          onClick={() => {
            setSelectedPersonId(person.id);
            if (hasChildren) toggleExpanded(person.id);
          }}
          style={{
            padding: '8px',
            borderRadius: '4px',
            cursor: 'pointer',
            backgroundColor: selectedPersonId === person.id ? colors.indigo[100] : colors.transparent,
            marginBottom: '4px',
            border: selectedPersonId === person.id ? `2px solid ${colors.indigo[600]}` : `1px solid ${colors.gray[200]}`,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {hasChildren && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  toggleExpanded(person.id);
                }}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '16px',
                  width: '20px',
                  padding: 0,
                }}
              >
                {isExpanded ? '▼' : '▶'}
              </button>
            )}
            {!hasChildren && <div style={{ width: '20px' }} />}
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 'bold' }}>{person.name}</div>
              <div style={{ fontSize: '0.85em', color: colors.gray[600] }}>
                {calendarView === 'gregorian'
                  ? `${person.gregorian_year_born} – ${person.gregorian_year_died} (${person.lifespan_years} years)`
                  : `${person.zadok_year_born} – ${person.zadok_year_died} (${person.lifespan_years} years)`}
              </div>
            </div>
          </div>
        </div>
        {isExpanded && children.length > 0 && (
          <div>
            {children.map(child => (
              <TreeNode key={child.id} person={child} depth={depth + 1} />
            ))}
          </div>
        )}
      </div>
    );
  };

  // Get selected person
  const selectedPerson = getPerson(selectedPersonId);

  return (
    <div style={{ padding: '20px', maxWidth: '1400px', margin: '0 auto', fontFamily: 'system-ui, sans-serif' }}>
      <h1 style={{ marginBottom: '20px', color: colors.slate[900] }}>Biblical Genealogy Viewer</h1>

      {/* Controls */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '16px',
          marginBottom: '20px',
          padding: '16px',
          backgroundColor: colors.gray[50],
          borderRadius: '8px',
        }}
      >
        <div>
          <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold', fontSize: '0.9em' }}>
            Calendar View:
          </label>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => setCalendarView('gregorian')}
              style={{
                flex: 1,
                padding: '8px',
                border: calendarView === 'gregorian' ? `2px solid ${colors.indigo[600]}` : `1px solid ${colors.gray[300]}`,
                backgroundColor: calendarView === 'gregorian' ? colors.indigo[50] : colors.white,
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: calendarView === 'gregorian' ? 'bold' : 'normal',
              }}
            >
              Gregorian
            </button>
            <button
              onClick={() => setCalendarView('zadok')}
              style={{
                flex: 1,
                padding: '8px',
                border: calendarView === 'zadok' ? `2px solid ${colors.indigo[600]}` : `1px solid ${colors.gray[300]}`,
                backgroundColor: calendarView === 'zadok' ? colors.indigo[50] : colors.white,
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: calendarView === 'zadok' ? 'bold' : 'normal',
              }}
            >
              Zadok
            </button>
          </div>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold', fontSize: '0.9em' }}>
            Filter by Era:
          </label>
          <select
            value={filterEra}
            onChange={(e) => setFilterEra(e.target.value)}
            style={{
              width: '100%',
              padding: '8px',
              border: `1px solid ${colors.gray[300]}`,
              borderRadius: '4px',
              fontSize: '0.9em',
            }}
          >
            <option value="all">All Eras</option>
            <option value="Antediluvian">Antediluvian</option>
            <option value="Antediluvian/Flood">Flood</option>
            <option value="Post-Flood">Post-Flood</option>
            <option value="Patriarchal">Patriarchal</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold', fontSize: '0.9em' }}>
            Filter by Gender:
          </label>
          <select
            value={filterGender}
            onChange={(e) => setFilterGender(e.target.value)}
            style={{
              width: '100%',
              padding: '8px',
              border: `1px solid ${colors.gray[300]}`,
              borderRadius: '4px',
              fontSize: '0.9em',
            }}
          >
            <option value="all">All Genders</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold', fontSize: '0.9em' }}>
            Search by Name:
          </label>
          <input
            type="text"
            placeholder="Search name or Hebrew..."
            value={filterName}
            onChange={(e) => setFilterName(e.target.value)}
            style={{
              width: '100%',
              padding: '8px',
              border: `1px solid ${colors.gray[300]}`,
              borderRadius: '4px',
              fontSize: '0.9em',
            }}
          />
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold', fontSize: '0.9em' }}>
            Find People Alive in Year:
          </label>
          <input
            type="number"
            placeholder="Enter year (e.g., -2000)"
            value={livingYearQuery}
            onChange={(e) => setLivingYearQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '8px',
              border: `1px solid ${colors.gray[300]}`,
              borderRadius: '4px',
              fontSize: '0.9em',
            }}
          />
        </div>
      </div>

      {/* Tabs */}
      <div style={{ marginBottom: '20px', borderBottom: `2px solid ${colors.gray[200]}`, display: 'flex', gap: '8px' }}>
        {['tree', 'timeline', 'living', 'lineage', 'details'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '12px 20px',
              border: 'none',
              backgroundColor: activeTab === tab ? colors.indigo[600] : colors.transparent,
              color: activeTab === tab ? colors.white : colors.gray[600],
              cursor: 'pointer',
              fontWeight: activeTab === tab ? 'bold' : 'normal',
              borderRadius: '4px 4px 0 0',
              textTransform: 'capitalize',
            }}
          >
            {tab === 'timeline' ? 'Gantt Timeline' : tab === 'living' ? 'Living in Year' : tab === 'lineage' ? 'Lineages' : tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div style={{ minHeight: '400px' }}>
        {/* Tree View */}
        {activeTab === 'tree' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div style={{ borderRight: `1px solid ${colors.gray[200]}`, paddingRight: '16px' }}>
              <h2 style={{ fontSize: '1.2em', marginBottom: '16px' }}>Family Tree (Adam → Abraham)</h2>
              <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
                <TreeNode person={getPerson('adam')} />
              </div>
            </div>
            {selectedPerson && (
              <div style={{ paddingLeft: '16px' }}>
                <h2 style={{ fontSize: '1.2em', marginBottom: '16px' }}>
                  {selectedPerson.name}
                </h2>
                <div style={{ backgroundColor: colors.gray[100], padding: '16px', borderRadius: '8px' }}>
                  <p>
                    <strong>Title:</strong> {selectedPerson.title}
                  </p>
                  <p>
                    <strong>Era:</strong> {selectedPerson.era}
                  </p>
                  <p>
                    <strong>Lifespan:</strong> {selectedPerson.lifespan_years} years
                  </p>
                  <p>
                    <strong>Born:</strong>{' '}
                    {calendarView === 'gregorian'
                      ? `${selectedPerson.gregorian_year_born} AD`
                      : `${selectedPerson.zadok_year_born} (Zadok)`}
                  </p>
                  <p>
                    <strong>Died:</strong>{' '}
                    {selectedPerson.gregorian_year_died !== null
                      ? calendarView === 'gregorian'
                        ? `${selectedPerson.gregorian_year_died} AD`
                        : `${selectedPerson.zadok_year_died} (Zadok)`
                      : 'Unknown'}
                  </p>
                  <p>
                    <strong>Significance:</strong> Level {selectedPerson.significance_level}/3
                  </p>
                  <p>
                    <strong>Role:</strong> {selectedPerson.prophetic_role}
                  </p>
                  {selectedPerson.tags.length > 0 && (
                    <div>
                      <strong>Tags:</strong>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '8px' }}>
                        {selectedPerson.tags.map(tag => (
                          <span
                            key={tag}
                            style={{
                              backgroundColor: colors.blue[50],
                              color: colors.blue[800],
                              padding: '4px 8px',
                              borderRadius: '4px',
                              fontSize: '0.85em',
                            }}
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {selectedPerson.major_events.length > 0 && (
                    <div style={{ marginTop: '16px' }}>
                      <strong>Major Events:</strong>
                      <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                        {selectedPerson.major_events.map((event, idx) => (
                          <li key={idx} style={{ marginBottom: '8px', fontSize: '0.9em' }}>
                            <strong>{event.event}</strong> (
                            {calendarView === 'gregorian'
                              ? `${event.gregorian_year} AD`
                              : `${event.zadok_year} Z`}
                            ): {event.description}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Gantt Timeline */}
        {activeTab === 'timeline' && (
          <div>
            <h2 style={{ marginBottom: '16px' }}>Timeline (Patriarch Lifespans)</h2>
            
            {/* Zoom Controls */}
            <div style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', backgroundColor: colors.blue.light, borderRadius: '8px', border: `1px solid ${colors.blue[100]}` }}>
              <button
                onClick={() => setGanttZoom(Math.max(0.5, ganttZoom - 0.1))}
                style={{
                  padding: '6px 12px',
                  backgroundColor: colors.blue[500],
                  color: colors.white,
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '0.9em',
                  fontWeight: 'bold'
                }}
              >
                − Zoom Out
              </button>
              
              <input
                type="range"
                min="0.5"
                max="2"
                step="0.1"
                value={ganttZoom}
                onChange={(e) => setGanttZoom(parseFloat(e.target.value))}
                style={{
                  flex: 1,
                  height: '6px',
                  cursor: 'pointer'
                }}
              />
              
              <button
                onClick={() => setGanttZoom(Math.min(2, ganttZoom + 0.1))}
                style={{
                  padding: '6px 12px',
                  backgroundColor: colors.blue[500],
                  color: colors.white,
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '0.9em',
                  fontWeight: 'bold'
                }}
              >
                + Zoom In
              </button>
              
              <span style={{ fontSize: '0.9em', fontWeight: 'bold', color: colors.slate[900], minWidth: '60px' }}>
                {Math.round(ganttZoom * 100)}%
              </span>
            </div>

            <div style={{ display: 'flex', gap: '0', backgroundColor: colors.gray[50], borderRadius: '8px', border: `1px solid ${colors.gray[200]}`, overflow: 'hidden' }}>
              {/* Fixed Names Column */}
              <div style={{ width: '150px', flexShrink: 0, borderRight: `2px solid ${colors.gray[300]}`, backgroundColor: colors.white, overflowY: 'auto' }}>
                {/* Header */}
                <div style={{
                  padding: '12px 8px',
                  fontWeight: 'bold',
                  borderBottom: `2px solid ${colors.gray[300]}`,
                  backgroundColor: colors.gray[100],
                  position: 'sticky',
                  top: 0,
                  zIndex: 10
                }}>
                  Name
                </div>
                {/* Names */}
                {filteredPeople.map(person => {
                  const startYear = person.gregorian_year_born;
                  const endYear = person.gregorian_year_died;
                  if (startYear === null || endYear === null) return null;

                  return (
                    <div
                      key={person.id}
                      onClick={() => {
                        setSelectedPersonId(person.id);
                        setActiveTab('details');
                      }}
                      style={{
                        padding: '6px 8px',
                        height: '36px',
                        display: 'flex',
                        alignItems: 'center',
                        fontSize: '0.9em',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        color: colors.blue[600],
                        cursor: 'pointer',
                        textDecoration: 'underline',
                        fontWeight: '500',
                        borderBottom: `1px solid ${colors.gray[200]}`,
                        backgroundColor: selectedPersonId === person.id ? colors.blue[50] : colors.white,
                        transition: 'backgroundColor 0.2s'
                      }}
                      title={`Click to view ${person.name}'s details`}
                    >
                      {person.name}
                    </div>
                  );
                })}
              </div>

              {/* Scrollable Timeline Area */}
              <div style={{ flex: 1, overflowX: 'auto', overflowY: 'auto', position: 'relative' }}>
                <div style={{ minWidth: `${800 * ganttZoom}px`, minHeight: '100%' }}>
                  {/* Year Scale Header */}
                  <div style={{
                    display: 'flex',
                    height: '50px',
                    paddingBottom: '8px',
                    borderBottom: `2px solid ${colors.gray[300]}`,
                    backgroundColor: colors.gray[100],
                    position: 'sticky',
                    top: 0,
                    zIndex: 9
                  }}>
                    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
                      {Array.from({ length: Math.ceil(((-1800 - (-4100)) / 200) * ganttZoom) + 1 }).map((_, i) => {
                        const gregorianYear = -4100 + (i * 200 / ganttZoom);
                        const zadokYear = gregorianToZadok(gregorianYear);
                        const displayYear = calendarView === 'gregorian' ? gregorianYear : zadokYear;
                        const percentPos = ((gregorianYear - (-4100)) / ((-1800) - (-4100))) * 100;
                        return (
                          <div
                            key={i}
                            style={{
                              position: 'absolute',
                              left: `${percentPos}%`,
                              display: 'flex',
                              flexDirection: 'column',
                              alignItems: 'center',
                              transform: 'translateX(-50%)',
                              height: '100%',
                              justifyContent: 'flex-end',
                              paddingBottom: '4px'
                            }}
                          >
                            <div style={{ height: '6px', width: '2px', backgroundColor: colors.gray[500], marginBottom: '2px' }} />
                            <div style={{ fontSize: '0.7em', color: colors.gray[500], fontWeight: 'bold', whiteSpace: 'nowrap' }}>
                              {displayYear}{calendarView === 'essene' ? 'E' : ''}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Person Bars */}
                  {filteredPeople.map(person => {
                    const startYear = person.gregorian_year_born;
                    const endYear = person.gregorian_year_died;
                    if (startYear === null || endYear === null) return null;

                    const minYear = -4100;
                    const maxYear = -1800;
                    const totalYears = maxYear - minYear;
                    const startPercent = ((startYear - minYear) / totalYears) * 100;
                    const width = ((endYear - startYear) / totalYears) * 100;

                    return (
                      <div key={person.id} style={{ position: 'relative', height: '36px', display: 'flex', alignItems: 'center', borderBottom: `1px solid ${colors.gray[200]}`, backgroundColor: selectedPersonId === person.id ? colors.blue[50] : colors.white }}>
                        <div style={{ position: 'relative', width: '100%', height: '28px', backgroundColor: colors.gray[200], marginLeft: '8px', marginRight: '8px', borderRadius: '4px', display: 'flex', alignItems: 'center' }}>
                          <div
                            onClick={() => {
                              setSelectedPersonId(person.id);
                              setActiveTab('details');
                            }}
                            style={{
                              position: 'absolute',
                              left: `${startPercent}%`,
                              width: `${width}%`,
                              height: '100%',
                              backgroundColor: person.lineages.includes('jesus_line') ? colors.accent.red : colors.blue[500],
                              borderRadius: '4px',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              color: colors.white,
                              fontSize: '0.75em',
                              overflow: 'hidden',
                              cursor: 'pointer',
                              transition: 'opacity 0.2s',
                              opacity: selectedPersonId === person.id ? 1 : 0.8,
                              border: selectedPersonId === person.id ? `2px solid ${colors.slate[900]}` : `1px solid ${colors.overlay.darkSubtle}`
                            }}
                            title={calendarView === 'gregorian' ? `${person.name}: ${startYear} to ${endYear} (${person.lifespan_years} years)` : `${person.name}: ${person.zadok_year_born} to ${person.zadok_year_died} Z (${person.lifespan_years} years)`}
                            onMouseEnter={(e) => e.target.style.opacity = '1'}
                            onMouseLeave={(e) => e.target.style.opacity = selectedPersonId === person.id ? '1' : '0.8'}
                          >
                            {width > 5 && <span style={{ whiteSpace: 'nowrap', fontWeight: 'bold' }}>{person.lifespan_years}y</span>}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Legend */}
            <div style={{ marginTop: '16px', fontSize: '0.85em', color: colors.gray[600] }}>
              <div>
                <span
                  style={{
                    display: 'inline-block',
                    width: '16px',
                    height: '16px',
                    backgroundColor: colors.accent.red,
                    borderRadius: '2px',
                    marginRight: '8px',
                  }}
                />
                Jesus's Lineage
              </div>
              <div>
                <span
                  style={{
                    display: 'inline-block',
                    width: '16px',
                    height: '16px',
                    backgroundColor: colors.blue[500],
                    borderRadius: '2px',
                    marginRight: '8px',
                  }}
                />
                Other Patriarchs
              </div>
              <div style={{ marginTop: '8px', fontSize: '0.8em', color: colors.gray.light, fontStyle: 'italic' }}>
                Click name or bar to view person details
              </div>
            </div>
          </div>
        )}

        {/* Living in Year */}
        {activeTab === 'living' && (
          <div>
            <h2 style={{ marginBottom: '16px' }}>Who Lived in a Specific Year?</h2>
            {livingYearQuery && (
              <div style={{ padding: '16px', backgroundColor: colors.gray[100], borderRadius: '8px' }}>
                <h3 style={{ marginBottom: '12px' }}>
                  People alive in {livingYearQuery} AD:
                </h3>
                {getPeopleAliveInYear(parseInt(livingYearQuery)).length > 0 ? (
                  <ul style={{ listStyle: 'none', padding: 0 }}>
                    {getPeopleAliveInYear(parseInt(livingYearQuery)).map(person => (
                      <li key={person.id} style={{ padding: '8px', borderBottom: `1px solid ${colors.gray[200]}` }}>
                        <strong>{person.name}</strong> ({person.gregorian_year_born} – {person.gregorian_year_died})
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ color: colors.gray[600] }}>No one in our genealogy lived in that year.</p>
                )}
              </div>
            )}
            {!livingYearQuery && (
              <p style={{ color: colors.gray[600] }}>Enter a year above to see who was alive at that time.</p>
            )}
          </div>
        )}

        {/* Lineages */}
        {activeTab === 'lineage' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div>
              <h2 style={{ fontSize: '1.2em', marginBottom: '16px' }}>Available Lineages</h2>
              {Object.entries(genealogyData.lineages).map(([key, lineage]) => (
                <div
                  key={key}
                  onClick={() => setSelectedLineage(key)}
                  style={{
                    padding: '12px',
                    marginBottom: '8px',
                    backgroundColor: selectedLineage === key ? colors.indigo[50] : colors.gray[50],
                    border: selectedLineage === key ? `2px solid ${colors.indigo[600]}` : `1px solid ${colors.gray[300]}`,
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }}
                >
                  <div style={{ fontWeight: 'bold', color: lineage.color }}>{lineage.name}</div>
                  <div style={{ fontSize: '0.85em', color: colors.gray[600], marginTop: '4px' }}>
                    {lineage.description}
                  </div>
                </div>
              ))}
            </div>
            <div>
              <h2 style={{ fontSize: '1.2em', marginBottom: '16px' }}>
                {genealogyData.lineages[selectedLineage]?.name}
              </h2>
              <div style={{ backgroundColor: colors.gray[100], padding: '16px', borderRadius: '8px' }}>
                <p style={{ marginBottom: '12px' }}>
                  {genealogyData.lineages[selectedLineage]?.description}
                </p>
                <h3 style={{ marginTop: '16px', marginBottom: '8px' }}>People in this lineage:</h3>
                <ul style={{ listStyle: 'none', padding: 0 }}>
                  {filteredPeople
                    .filter(p => p.lineages.includes(selectedLineage))
                    .map(person => (
                      <li key={person.id} style={{ padding: '4px 0', fontSize: '0.9em' }}>
                        {person.name} ({person.lifespan_years} years)
                      </li>
                    ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Details Panel */}
        {activeTab === 'details' && selectedPerson && (
          <div style={{ maxWidth: '900px' }}>
            <h2 style={{ marginBottom: '6px' }}>{selectedPerson.name}</h2>
            
            {/* Hebrew Name Section */}
            {selectedPerson.name_hebrew && (
              <div style={{ 
                marginBottom: '20px', 
                padding: '12px 16px', 
                backgroundColor: colors.indigo.light, 
                borderLeft: `4px solid ${colors.indigo[600]}`,
                borderRadius: '4px'
              }}>
                <div style={{ fontFamily: 'serif', fontSize: '1.4em', marginBottom: '6px', color: colors.slate[900], fontWeight: 'bold' }}>
                  {selectedPerson.name_hebrew}
                </div>
                <div style={{ fontSize: '0.95em', color: colors.indigo[600], marginBottom: '6px', fontWeight: '500' }}>
                  {selectedPerson.name_transliteration}
                </div>
                {selectedPerson.name_meaning && (
                  <div style={{ fontSize: '0.9em', color: colors.gray[600], fontStyle: 'italic' }}>
                    <strong>Meaning:</strong> {selectedPerson.name_meaning}
                  </div>
                )}
              </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              <div>
                <h3 style={{ marginBottom: '12px', color: colors.indigo[600] }}>Personal Information</h3>
                <div style={{ backgroundColor: colors.gray[100], padding: '16px', borderRadius: '8px' }}>
                  <p>
                    <strong>Full Title:</strong> {selectedPerson.title}
                  </p>
                  <p>
                    <strong>Data Classification:</strong> {selectedPerson.data_classification}
                  </p>
                  <p>
                    <strong>Era:</strong> {selectedPerson.era}
                  </p>
                  <p>
                    <strong>Prophetic Role:</strong> {selectedPerson.prophetic_role}
                  </p>
                  <p>
                    <strong>Significance Level:</strong> {selectedPerson.significance_level}/3
                  </p>
                </div>
              </div>
              <div>
                <h3 style={{ marginBottom: '12px', color: colors.indigo[600] }}>Lifespan</h3>
                <div style={{ backgroundColor: colors.gray[100], padding: '16px', borderRadius: '8px' }}>
                  <p>
                    <strong>Gregorian:</strong> {selectedPerson.gregorian_year_born} to{' '}
                    {selectedPerson.gregorian_year_died} AD
                  </p>
                  <p>
                    <strong>Zadok:</strong> {selectedPerson.zadok_year_born} to {selectedPerson.zadok_year_died}
                  </p>
                  <p>
                    <strong>Years Lived:</strong> {selectedPerson.lifespan_years}
                  </p>
                </div>
              </div>
            </div>

            {selectedPerson.major_events.length > 0 && (
              <div style={{ marginTop: '20px' }}>
                <h3 style={{ marginBottom: '12px', color: colors.indigo[600] }}>Major Events</h3>
                <div style={{ backgroundColor: colors.gray[100], padding: '16px', borderRadius: '8px' }}>
                  {selectedPerson.major_events.map((event, idx) => (
                    <div key={idx} style={{ marginBottom: '12px', borderBottom: `1px solid ${colors.gray[200]}`, paddingBottom: '12px' }}>
                      <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                        {event.event} ({event.gregorian_year} AD / {event.zadok_year} Z)
                      </div>
                      <div style={{ fontSize: '0.9em', color: colors.gray[600] }}>{event.description}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedPerson.bible_references.length > 0 && (
              <div style={{ marginTop: '20px' }}>
                <h3 style={{ marginBottom: '12px', color: colors.indigo[600] }}>Bible References</h3>
                <div style={{ backgroundColor: colors.accent.amber, padding: '16px', borderRadius: '8px' }}>
                  <ul style={{ listStyle: 'none', padding: 0 }}>
                    {selectedPerson.bible_references.map((ref, idx) => (
                      <li key={idx} style={{ marginBottom: '8px', fontSize: '0.9em' }}>
                        <BibleReference text={ref} version="esv" site="blueletterbible" />
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {selectedPerson.children.length > 0 && (
              <div style={{ marginTop: '20px' }}>
                <h3 style={{ marginBottom: '12px', color: colors.indigo[600] }}>Children</h3>
                <div style={{ backgroundColor: colors.gray[100], padding: '16px', borderRadius: '8px' }}>
                  <ul style={{ listStyle: 'none', padding: 0 }}>
                    {selectedPerson.children.map(childId => {
                      const child = getPerson(childId);
                      return (
                        <li key={childId} style={{ marginBottom: '8px' }}>
                          <strong>{child.name}</strong> ({child.lifespan_years} years)
                        </li>
                      );
                    })}
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default GenealogyViewer;
