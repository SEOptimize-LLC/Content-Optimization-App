"""
Semantic Content Network Builder
Builds internal linking strategy and content network structure.
Based on Koray's Semantic SEO framework.
"""

import networkx as nx
from sentence_transformers import SentenceTransformer, util
from typing import Dict, List, Tuple, Optional
import json

try:
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Error loading embedder: {e}")
    embedder = None


class SemanticContentNetwork:
    """Build and manage semantic content network."""

    def __init__(self, topical_map: Dict):
        """
        Initialize network builder.

        Args:
            topical_map: Complete topical map structure
        """
        self.topical_map = topical_map
        self.graph = nx.DiGraph()  # Directed graph for link flow
        self.embedder = embedder

    def build_network(self) -> Dict:
        """
        Build complete semantic content network.

        Returns:
            Network structure with nodes, edges, and linking strategy
        """
        # Create network nodes from topical map
        self._create_nodes()

        # Create edges (internal links) based on semantic relationships
        self._create_edges()

        # Identify root document
        root_document = self._identify_root_document()

        # Generate linking strategy
        linking_strategy = self._generate_linking_strategy()

        # Calculate network metrics
        metrics = self._calculate_network_metrics()

        return {
            'graph': self.graph,
            'root_document': root_document,
            'linking_strategy': linking_strategy,
            'metrics': metrics,
            'visualization_data': self._export_for_visualization()
        }

    def _create_nodes(self):
        """Create network nodes from topical map."""
        info_tree = self.topical_map.get('information_tree', {})

        # Root node
        root = info_tree.get('root', {})
        if root:
            self.graph.add_node('root', **{
                'title': root.get('title', ''),
                'macro_context': root.get('macro_context', ''),
                'type': 'root',
                'priority': 'highest',
                'pagerank_target': True
            })

        # Core nodes (monetization focus)
        for i, branch in enumerate(info_tree.get('core_branches', [])):
            node_id = f"core_{i}"
            self.graph.add_node(node_id, **{
                'title': branch.get('title', ''),
                'attribute': branch.get('attribute', ''),
                'macro_context': branch.get('macro_context', ''),
                'type': 'core',
                'priority': 'high',
                'children': branch.get('children', [])
            })

        # Author nodes (broader coverage)
        for i, branch in enumerate(info_tree.get('author_branches', [])):
            node_id = f"author_{i}"
            self.graph.add_node(node_id, **{
                'title': branch.get('title', ''),
                'attribute': branch.get('attribute', ''),
                'macro_context': branch.get('macro_context', ''),
                'type': 'author',
                'priority': 'medium',
                'children': branch.get('children', [])
            })

    def _create_edges(self):
        """Create edges (internal links) based on semantic relationships."""
        nodes = list(self.graph.nodes(data=True))

        # 1. Root links to all core nodes (highest priority)
        for node_id, node_data in nodes:
            if node_data['type'] == 'core':
                self.graph.add_edge('root', node_id, **{
                    'weight': 1.0,
                    'priority': 'highest',
                    'anchor_context': node_data['attribute'],
                    'placement': 'main_content'
                })

        # 2. Core nodes link to related core nodes (semantic similarity)
        core_nodes = [(nid, ndata) for nid, ndata in nodes if ndata['type'] == 'core']

        for i, (node_id1, node_data1) in enumerate(core_nodes):
            for node_id2, node_data2 in core_nodes:
                if node_id1 != node_id2:
                    # Calculate semantic similarity
                    similarity = self._calculate_similarity(
                        node_data1['macro_context'],
                        node_data2['macro_context']
                    )

                    if similarity > 0.4:  # Threshold for related content
                        self.graph.add_edge(node_id1, node_id2, **{
                            'weight': similarity,
                            'priority': 'high',
                            'anchor_context': node_data2['attribute'],
                            'placement': 'body',
                            'semantic_similarity': similarity
                        })

        # 3. Core nodes link to relevant author nodes
        author_nodes = [(nid, ndata) for nid, ndata in nodes if ndata['type'] == 'author']

        for core_id, core_data in core_nodes:
            for author_id, author_data in author_nodes:
                similarity = self._calculate_similarity(
                    core_data['macro_context'],
                    author_data['macro_context']
                )

                if similarity > 0.35:
                    self.graph.add_edge(core_id, author_id, **{
                        'weight': similarity * 0.8,  # Lower weight for core->author
                        'priority': 'medium',
                        'anchor_context': author_data['attribute'],
                        'placement': 'supplementary',
                        'semantic_similarity': similarity
                    })

        # 4. Author nodes link back to related core nodes (for PageRank flow)
        for author_id, author_data in author_nodes:
            for core_id, core_data in core_nodes:
                similarity = self._calculate_similarity(
                    author_data['macro_context'],
                    core_data['macro_context']
                )

                if similarity > 0.4:
                    self.graph.add_edge(author_id, core_id, **{
                        'weight': similarity,
                        'priority': 'medium',
                        'anchor_context': core_data['attribute'],
                        'placement': 'body'
                    })

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        if not self.embedder:
            return 0.5  # Default

        emb1 = self.embedder.encode([text1])[0]
        emb2 = self.embedder.encode([text2])[0]

        return util.cos_sim(emb1, emb2).item()

    def _identify_root_document(self) -> Dict:
        """Identify and return root document details."""
        if 'root' in self.graph.nodes:
            root_data = self.graph.nodes['root']
            return {
                'node_id': 'root',
                'title': root_data['title'],
                'macro_context': root_data['macro_context'],
                'outbound_links': list(self.graph.successors('root')),
                'link_count': self.graph.out_degree('root')
            }
        return {}

    def _generate_linking_strategy(self) -> Dict:
        """
        Generate comprehensive internal linking strategy.

        Returns:
            Linking strategy for each node
        """
        strategy = {
            'nodes': [],
            'global_rules': []
        }

        for node_id, node_data in self.graph.nodes(data=True):
            # Get outbound links
            outbound = list(self.graph.successors(node_id))
            outbound_details = []

            for target_id in outbound:
                edge_data = self.graph.edges[node_id, target_id]
                target_data = self.graph.nodes[target_id]

                outbound_details.append({
                    'target': target_data['title'],
                    'anchor_text': edge_data['anchor_context'],
                    'placement': edge_data['placement'],
                    'priority': edge_data['priority'],
                    'weight': edge_data['weight']
                })

            # Sort by priority and weight
            priority_order = {'highest': 3, 'high': 2, 'medium': 1, 'low': 0}
            outbound_details.sort(
                key=lambda x: (priority_order[x['priority']], x['weight']),
                reverse=True
            )

            # Get inbound links
            inbound = list(self.graph.predecessors(node_id))

            strategy['nodes'].append({
                'node_id': node_id,
                'title': node_data['title'],
                'type': node_data['type'],
                'outbound_links': outbound_details[:8],  # Max 8 outbound links
                'inbound_count': len(inbound),
                'instructions': self._generate_link_instructions(
                    node_data,
                    outbound_details
                )
            })

        # Global linking rules
        strategy['global_rules'] = [
            {
                'rule': 'ROOT_PRIORITY',
                'description': 'Most important anchor tags in root document',
                'implementation': 'Place highest-priority links in introduction of root document'
            },
            {
                'rule': 'LINK_DISTANCE',
                'description': 'Maintain distance between internal links',
                'implementation': 'Generally one link per heading/section'
            },
            {
                'rule': 'CONTEXTUAL_RELEVANCE',
                'description': 'Links must be contextually relevant and clickable',
                'implementation': 'Use natural anchor text that fits sentence flow'
            },
            {
                'rule': 'TOP_PLACEMENT',
                'description': 'Links in top of main content have higher weight',
                'implementation': 'Place important links early in content'
            }
        ]

        return strategy

    def _generate_link_instructions(self,
                                   node_data: Dict,
                                   outbound_details: List[Dict]) -> List[str]:
        """Generate specific linking instructions for a node."""
        instructions = []

        if node_data['type'] == 'root':
            instructions.append('This is the root document - it connects to all core attributes')
            instructions.append('Place most important links in the introduction')
            instructions.append(f'Include {len(outbound_details)} strategic links to core content')

        elif node_data['type'] == 'core':
            instructions.append('Core content - focus on monetization-related links')
            instructions.append('Link back to root document in introduction')
            instructions.append('Link to related core attributes in body')
            if any(link['placement'] == 'supplementary' for link in outbound_details):
                instructions.append('Include supplementary links to author content at end')

        elif node_data['type'] == 'author':
            instructions.append('Author content - broader topical coverage')
            instructions.append('Link back to relevant core content')
            instructions.append('Help distribute PageRank to core sections')

        # Specific anchor text guidance
        if outbound_details:
            top_link = outbound_details[0]
            instructions.append(
                f'Primary anchor text: "{top_link["anchor_text"]}" linking to {top_link["target"]}'
            )

        return instructions

    def _calculate_network_metrics(self) -> Dict:
        """Calculate network health metrics."""
        metrics = {}

        # Basic metrics
        metrics['total_nodes'] = self.graph.number_of_nodes()
        metrics['total_edges'] = self.graph.number_of_edges()
        metrics['average_degree'] = sum(dict(self.graph.degree()).values()) / metrics['total_nodes'] if metrics['total_nodes'] > 0 else 0

        # PageRank (simulated)
        try:
            pagerank = nx.pagerank(self.graph)
            metrics['pagerank_scores'] = {
                node: round(score, 4)
                for node, score in sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
            }
        except:
            metrics['pagerank_scores'] = {}

        # Network density
        metrics['density'] = nx.density(self.graph)

        # Identify hubs (nodes with many outbound links)
        out_degrees = dict(self.graph.out_degree())
        metrics['hub_nodes'] = [
            {'node': node, 'out_degree': degree}
            for node, degree in sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        return metrics

    def _export_for_visualization(self) -> Dict:
        """Export network data for visualization."""
        nodes = []
        edges = []

        for node_id, node_data in self.graph.nodes(data=True):
            nodes.append({
                'id': node_id,
                'label': node_data.get('title', node_id),
                'type': node_data.get('type', 'unknown'),
                'priority': node_data.get('priority', 'low')
            })

        for source, target, edge_data in self.graph.edges(data=True):
            edges.append({
                'source': source,
                'target': target,
                'weight': edge_data.get('weight', 0.5),
                'priority': edge_data.get('priority', 'medium')
            })

        return {
            'nodes': nodes,
            'edges': edges,
            'format': 'graph_json'
        }

    def export_to_markdown(self, network_data: Dict) -> str:
        """Export network to Markdown."""
        md = "# Semantic Content Network\n\n"

        # Root document
        root = network_data['root_document']
        if root:
            md += f"## Root Document\n"
            md += f"**{root['title']}**\n\n"
            md += f"- Macro Context: {root['macro_context']}\n"
            md += f"- Outbound Links: {root['link_count']}\n\n"

        # Network metrics
        metrics = network_data['metrics']
        md += "## Network Metrics\n"
        md += f"- Total Pages: {metrics['total_nodes']}\n"
        md += f"- Total Links: {metrics['total_edges']}\n"
        md += f"- Average Links per Page: {metrics['average_degree']:.1f}\n"
        md += f"- Network Density: {metrics['density']:.2f}\n\n"

        # Linking strategy
        strategy = network_data['linking_strategy']
        md += "## Linking Strategy\n\n"

        for node in strategy['nodes'][:10]:  # Top 10 nodes
            md += f"### {node['title']}\n"
            md += f"**Type:** {node['type']}\n\n"

            if node['outbound_links']:
                md += "**Outbound Links:**\n"
                for link in node['outbound_links'][:5]:
                    md += f"- → {link['target']}\n"
                    md += f"  - Anchor: \"{link['anchor_text']}\"\n"
                    md += f"  - Placement: {link['placement']}\n"

            md += "\n"

        return md


def build_semantic_network(topical_map: Dict) -> Dict:
    """
    Main function to build semantic content network.

    Args:
        topical_map: Complete topical map structure

    Returns:
        Complete network with linking strategy
    """
    builder = SemanticContentNetwork(topical_map)
    network_data = builder.build_network()

    # Add markdown export
    network_data['markdown'] = builder.export_to_markdown(network_data)

    return network_data
