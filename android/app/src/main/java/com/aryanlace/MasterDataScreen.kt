package com.aryanlace

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

private data class MasterUiModel(
    val id: Int,
    val entityType: String,
    val code: String,
    val name: String,
    val description: String?,
    val isActive: Boolean,
    val metadata: String,
)

@Composable
fun MasterDataScreen() {
    val sampleMasters = remember {
        listOf(
            MasterUiModel(
                id = 1,
                entityType = "machine",
                code = "M-001",
                name = "Machine 1",
                description = "Primary production machine",
                isActive = true,
                metadata = "{""status"" : "ready"}"
            ),
            MasterUiModel(
                id = 2,
                entityType = "employee",
                code = "E-010",
                name = "Ravi Kumar",
                description = "Machine operator",
                isActive = true,
                metadata = "{""hourlyRate"" : 220}"
            ),
            MasterUiModel(
                id = 3,
                entityType = "item",
                code = "ITM-A",
                name = "Item A",
                description = "Standard lace item",
                isActive = true,
                metadata = "{""stripsPerBunch"" : 24, ""standardTimePerBunch"" : 15}"
            ),
            MasterUiModel(
                id = 4,
                entityType = "job_worker",
                code = "JW-001",
                name = "Packing Worker 1",
                description = "Packing and finishing assignment",
                isActive = true,
                metadata = "{""normalDailyCapacity"" : 250}"
            ),
            MasterUiModel(
                id = 5,
                entityType = "bobbin",
                code = "BB-RED",
                name = "Red Bobbin",
                description = "Required for production runs",
                isActive = true,
                metadata = "{""colour"" : "red"}"
            ),
        )
    }

    var selectedType by remember { mutableStateOf("machine") }
    var searchQuery by remember { mutableStateOf("") }
    var showInactive by remember { mutableStateOf(false) }
    var formCode by remember { mutableStateOf("") }
    var formName by remember { mutableStateOf("") }
    var formDescription by remember { mutableStateOf("") }
    var formMetadata by remember { mutableStateOf("") }

    val filteredMasters = remember(sampleMasters, selectedType, searchQuery, showInactive) {
        sampleMasters.filter { master ->
            val matchesType = master.entityType == selectedType
            val matchesSearch = searchQuery.isBlank() ||
                master.code.contains(searchQuery, ignoreCase = true) ||
                master.name.contains(searchQuery, ignoreCase = true)
            val matchesStatus = showInactive || master.isActive
            matchesType && matchesSearch && matchesStatus
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text(text = "Master Data Management", style = MaterialTheme.typography.headlineMedium)
        Text(text = "Dynamic masters for machines, employees, job workers, items, and bobbins")

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            listOf("machine", "employee", "job_worker", "item", "bobbin").forEach { type ->
                FilterChip(
                    selected = selectedType == type,
                    onClick = { selectedType = type },
                    label = { Text(type.replaceFirstChar { it.uppercase() }) }
                )
            }
        }

        OutlinedTextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            label = { Text("Search by code or name") },
            modifier = Modifier.fillMaxWidth()
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(text = "Show inactive records")
            Switch(checked = showInactive, onCheckedChange = { showInactive = it })
        }

        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(text = "Create or update a master", style = MaterialTheme.typography.titleMedium)
                OutlinedTextField(value = selectedType, onValueChange = { selectedType = it }, label = { Text("Entity type") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = formCode, onValueChange = { formCode = it }, label = { Text("Code") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = formName, onValueChange = { formName = it }, label = { Text("Name") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = formDescription, onValueChange = { formDescription = it }, label = { Text("Description") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = formMetadata, onValueChange = { formMetadata = it }, label = { Text("Metadata") }, modifier = Modifier.fillMaxWidth())
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                    Text(text = "Active")
                    Switch(checked = true, onCheckedChange = {})
                }
            }
        }

        Text(text = "Existing masters", style = MaterialTheme.typography.titleMedium)
        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(filteredMasters) { master ->
                Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
                    Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text(text = "${master.code} • ${master.name}", style = MaterialTheme.typography.titleSmall)
                        Text(text = master.description ?: "No description")
                        Text(text = "Type: ${master.entityType} | Status: ${if (master.isActive) "Active" else "Inactive"}")
                        Text(text = "Metadata: ${master.metadata}")
                    }
                }
            }
        }
    }
}
